from types import DynamicClassAttribute
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Citation, Crate, Entity, Organization, People

@registry.register_document
class CrateDocument(Document):
    entities = fields.NestedField(properties={
        'name': fields.TextField(),
        'entity_id': fields.TextField(),
        'description': fields.TextField(),
        'type': fields.ListField(fields.KeywordField()),
        'dateCreated': fields.DateField(),
        'dateModified': fields.DateField(),
        'programmingLanguage': fields.KeywordField(),
    })

    authors = fields.NestedField(properties={
        'ocrid': fields.TextField(),
        'name': fields.TextField(),
    })

    publisher = fields.NestedField(properties={
        'id': fields.TextField(),
        'name': fields.TextField(),
    })

    citation = fields.NestedField(properties={
        'id': fields.TextField(),
        'name': fields.TextField(),
    })

    keywords = fields.ListField(fields.TextField())
    identifier = fields.ListField(fields.TextField())
    license = fields.KeywordField()
    discipline = fields.ListField(fields.KeywordField())
    datePublished = fields.DateField()
    class Index:
        name = 'crates'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}
    
    class Django:
        model = Crate
        related_models = [Entity, People, Organization, Citation]
        fields = [
            'name',
            'description',
            'url',
        ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, People):
            return related_instance.crates.all()
        elif isinstance(related_instance, Organization):
            return related_instance.crates.all()
        elif isinstance(related_instance, Citation):
            return related_instance.crates.all()
        elif isinstance(related_instance, Entity):
            return related_instance.crate

# @registry.register_document
# class DataEntityDocument(Document):
#     class Index:
#         name = 'data_entities'
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}
        
#     class Django:
#         model = Entity
#         fields = [
#             'entity_id',
#             'name',
#             'type',
#             'description',
#             'dateCreated',
#             'dateModified',
#             'programmingLanguage',
#         ]
#         related_models = [Crate]
# @registry.register_document
# class CrateJsonDoc(Document):

#     data = fields.NestedField(dynamic=True)

#     def prepare_data(self, instance):
#         return instance.data

#     class Index:
#         name = 'cratejson'

#     class Django:
#         model = CrateJson
#         fields = []


# @registry.register_document
# class EntityJsonDoc(Document):

#     data = fields.ObjectField(dynamic=True)

#     def prepare_data(self, instance):
#         return instance.data

#     class Index:
#         name = 'entityjson'

#     class Django:
#         model = EntityJson
#         fields = []