import json
import os
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import AdditionalConfig
from weaviate.util import generate_uuid5

from src.utils.utils import rate_limit_function


class WeaviateDB:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = self._get_client()
        self.collection: weaviate.collections.Collection = rate_limit_function(
            self.client.collections.get, error_message="rate"
        )(self.collection_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def insert_many(self, data):
        logging.info(
            f"Inserting {len(data)} items into collection {self.collection_name}"
        )

        if len(data) == 0:
            return []
        return rate_limit_function(
            self.collection.data.insert_many, error_message="rate", max_retry_timer=100
        )(data)

    def delete_many(self, ids=None, filters=None):
        logging.info(
            f"Deleting items from collection {self.collection_name}, filters: {json.dumps(filters)}"
        )

        if ids is None and filters is None:
            raise Exception("Invalid delete_many call")

        if ids and len(ids) > 0:
            return rate_limit_function(
                self.collection.data.delete_many, error_message="rate"
            )(where=wvc.query.Filter.by_id().contains_any(ids))
        elif filters:
            return rate_limit_function(
                self.collection.data.delete_many, error_message="rate"
            )(where=self._filter_dict_to_filter(filters))

    def fetch(self, id=None, ids=None, filters=None, limit=50):
        if id is None and ids is None and filters is None and limit is None:
            raise Exception("Invalid fetch call")

        if filters is not None:
            if isinstance(filters, dict):
                filters = self._filter_dict_to_filter(filters)
            response = rate_limit_function(
                self.collection.query.fetch_objects, error_message="rate"
            )(filters=filters, limit=limit)
            return [item.properties for item in response.objects]
        elif ids is not None:
            if len(ids) == 0:
                return []
            response = self.collection.query.fetch_objects(
                filters=wvc.query.Filter.by_id().contains_any(ids), limit=len(ids)
            )
            return [item.properties for item in response.objects]
        elif limit is not None:
            response = rate_limit_function(
                self.collection.query.fetch_objects, error_message="rate"
            )(limit=limit)
            return [item.properties for item in response.objects]
        else:
            raise Exception("Fetch by id not implemented")

    def count(self, filters=None):
        if filters is None:
            return rate_limit_function(
                self.collection.aggregate.over_all, error_message="rate"
            )().total_count
        else:
            if isinstance(filters, dict):
                filters = self._filter_dict_to_filter(filters)
            return rate_limit_function(
                self.collection.aggregate.over_all, error_message="rate"
            )(filters=filters).total_count

    def hybrid_search(
        self,
        query: str,
        limit: int = 50,
        alpha: float = None,
        metadata: bool = False,
        filters: dict = None,
        threshold: float = 0.0,
    ):
        query_args = {"limit": limit, "query": query}

        if alpha is not None:
            query_args["alpha"] = alpha
        if metadata:
            query_args["return_metadata"] = wvc.query.MetadataQuery(score=True)
        if filters:
            query_args["filters"] = self._filter_dict_to_filter(filters)
            logging.debug(f"Filters applied: {query_args['filters']}")

        tries = 2
        for _ in range(tries):
            try:
                response = rate_limit_function(
                    self.collection.query.hybrid, error_message="rate"
                )(**query_args)
                ret = [item.properties for item in response.objects]
                break
            except Exception as e:
                logging.error(f"Error in hybrid search: {e}")
                if _ == tries - 1:
                    raise e

        for i, item in enumerate(response.objects):
            ret[i]["score"] = item.metadata.score if metadata else 1

        return [item for item in ret if item["score"] >= threshold]

    def _to_data(self, obj: dict):
        if "metadata" not in obj or "vec" not in obj or "id" not in obj:
            logging.error(f"Invalid vector db object: {obj}")
            raise Exception("Invalid vector db object")

        return wvc.data.DataObject(
            properties=obj["metadata"],
            vector=obj["vec"],
            uuid=generate_uuid5({"id": obj["id"]}),
        )

    def collection_exists(self, collection_name=None):
        collection_name = collection_name if collection_name else self.collection_name
        return self.client.collections.exists(collection_name)

    def delete_collection(self, collection_name=None):
        collection_name = collection_name if collection_name else self.collection_name
        logging.info(f"Deleting collection {collection_name}")
        return rate_limit_function(
            self.client.collections.delete, error_message="rate"
        )(collection_name)

    def _get_client(self) -> weaviate.client.Client:
        headers = {"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}

        self.client: weaviate.client.Client = rate_limit_function(
            weaviate.connect_to_wcs, error_message="rate"
        )(
            cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(
                os.getenv("WEAVIATE_CLIENT_SECRET")
            ),
            headers=headers,
            skip_init_checks=True,
            additional_config=AdditionalConfig(timeout=(60, 180)),
        )

        if not self.client.collections.exists(self.collection_name):
            self._create_collection()

        return self.client

    def _create_collection(self):
        try:
            self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=self.get_vectorizor(),
                properties=self.get_collection_properties(self.collection_name),
            )
        except weaviate.exceptions.UnexpectedStatusCodeError as e:
            logging.warning(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logging.error(f"Error creating collection {self.collection_name}: {e}")
            if "already exists" in str(e):
                logging.warning(f"Collection {self.collection_name} already exists")
            else:
                raise e

    def get_vectorizor(self):
        return wvc.config.Configure.Vectorizer.text2vec_openai()

    def _filter_dict_to_filter(self, filters_dict):
        prop = list(filters_dict.keys())[0]
        operator = list(filters_dict[prop].keys())[0]
        value = filters_dict[prop][operator]
        filters_dict.pop(prop)

        if operator == "contains_any":
            filt = wvc.query.Filter.by_property(prop).contains_any(
                [str(v) for v in value]
            )
        elif operator == "contains_all":
            filt = wvc.query.Filter.by_property(prop).contains_all(
                [str(v) for v in value]
            )
        elif operator == "equal":
            filt = wvc.query.Filter.by_property(prop).equal(value)
        elif operator == "not_equal":
            filt = wvc.query.Filter.by_property(prop).not_equal(value)
        elif operator == "less_than":
            filt = wvc.query.Filter.by_property(prop).less_than(value)
        elif operator == "less_or_equal":
            filt = wvc.query.Filter.by_property(prop).less_or_equal(value)
        elif operator == "greater_than":
            filt = wvc.query.Filter.by_property(prop).greater_than(value)
        elif operator == "greater_or_equal":
            filt = wvc.query.Filter.by_property(prop).greater_or_equal(value)
        elif operator == "like":
            if isinstance(value, str):
                filt = wvc.query.Filter.by_property(prop).like(value)
            elif isinstance(value, list):
                filt = wvc.query.Filter.by_property(prop).like(value[0])
                for v in value[1:]:
                    filt = filt | wvc.query.Filter.by_property(prop).like(v)
        else:
            raise Exception("Invalid operator")

        return (
            filt
            if not filters_dict
            else filt & self._filter_dict_to_filter(filters_dict)
        )

    @staticmethod
    def get_collection_properties(collection_name: str):
        return WeaviateDB.default_collection_properties()

    @staticmethod
    def default_collection_properties():
        import weaviate.classes as wvc

        return [
            wvc.config.Property(
                name="object_id",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="timestamp",
                data_type=wvc.config.DataType.DATE,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="ingest_type",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="raw",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
        ]