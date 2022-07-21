from django.db import models
from rocrate.rocrate import ROCrate, Entity as RO_Entity, ContextEntity
from django.contrib.postgres.fields import ArrayField
import json

class Crate(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    datePublished = models.DateTimeField()
    authors = models.ManyToManyField('People', related_name='crates')
    publisher = models.ManyToManyField('Organization', related_name='crates')
    license = models.CharField(max_length=128, null=True, blank=True)
    keywords = ArrayField(
        models.CharField(max_length=128),
        null=True,
        blank=True,
    )
    url = models.CharField(max_length=128, null=True, blank=True)
    citation = models.ManyToManyField('Citation', related_name='crates')
    identifier = ArrayField(
        models.CharField(max_length=128, null=True, blank=True),
        null=True,
        blank=True,
    )
    models.CharField(max_length=128, null=True, blank=True)
    discipline =  ArrayField(
        models.CharField(max_length=128),
        null=True,
        blank=True,
    )

class Entity(models.Model):
    crate = models.ForeignKey(to="Crate", to_field="id", on_delete=models.CASCADE, related_name='entities')
    entity_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    type = ArrayField(
        models.CharField(max_length=32),
        size = 8
    ) #need to modify to array if only has one type
    dateCreated = models.DateTimeField(null=True, blank=True)
    dateModified = models.DateTimeField(null=True, blank=True)
    programmingLanguage = models.CharField(max_length=128, null=True, blank=True)

# class Person(models.Model):
#     id = models.CharField(max_length=128, primary_key=True)
#     name = models.CharField(max_length=128)
#     # class Meta:
#     #     unique_together=(("ocrid","name"))

class People(models.Model):
    ocrid = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    class Meta:
        unique_together=(("ocrid","name"))


class Organization(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=128)

class Citation(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=128)

# def delete_all():
#     crates = Crate.objects.all()
#     for c in crates:
#         c.delete()

# def init_crate(file) -> Crate:
#     rocrate = ROCrate(file)
#     crate = Crate()
#     crate.name = rocrate.name
#     crate.description = rocrate.description
#     crate.datePublished = rocrate.datePublished
#     if isinstance(rocrate.license, RO_Entity):
#         crate.license = rocrate.license['name']
#     else:
#         crate.license = rocrate.license

#     crate.keywords = rocrate.keywords
#     if "author" in rocrate.root_dataset:
#         crate.save()
#         if isinstance(rocrate.root_dataset['author'], list):
#             for author in rocrate.root_dataset['author']:
#                 au, created = Person.objects.get_or_create(id = author['@id'], name = author['name'])
#                 au.save()
#                 crate.authors.add(au)
#         else:
#             au, created = Person.objects.get_or_create(id = rocrate.root_dataset['author']['@id'], name = rocrate.root_dataset['author']['name'])
#             au.save()
#             crate.authors.add(au)
#     if "url" in rocrate.root_dataset:
#         crate.url = rocrate.root_dataset['url']
#     if "citation" in rocrate.root_dataset:
#         crate.citation = rocrate.root_dataset['citation']['@id']
#         crate.citation_name = rocrate.root_dataset['citation']['name']
#     if "identifier" in rocrate.root_dataset:
#         crate.identifier = rocrate.root_dataset['identifier']
#     crate.save()

#     for entity in rocrate.data_entities:
#         de = Entity()
#         de.crate = crate
#         de.entity_id = entity['@id']
#         if "name" in entity:
#             de.name = entity['name']
#         if "description" in entity:
#             de.description = entity['description']
#         type = entity['@type']
#         if isinstance(type, list):
#             de.type = type
#         else:
#             de.type = [type]
        
#         if "dateCreated" in entity:
#             de.dateCreated = entity['dateCreated']
#         if "dateModified" in entity:
#             de.dateModified = entity['dateModified']
#         if "programmingLanguage" in entity:
#             de.programmingLanguage = entity['programmingLanguage']['name']
#         de.save()
    
#     return crate