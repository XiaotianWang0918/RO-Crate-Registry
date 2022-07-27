from django.db import models
from datetime import date, datetime
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

def addTest(num, discipline):
    for i in range(1,num+1):
        crate = Crate()
        crate.name = "Test Case in %s No.%d"%(discipline,i)
        crate.description = "Test Case in %s No.%d"%(discipline,i)
        crate.datePublished = datetime.now()
        crate.license = "Apache-2.0"
        crate.keywords = ["test","%s"%discipline]
        crate.discipline = ["%s"%discipline]
        crate.url="#TestcaseIn%sNo%d"%(discipline, i)
        crate.identifier = ["#TestcaseIn%sNo%d"%(discipline, i)]
        crate.save()
        author = People.objects.filter(ocrid="Test111", name="Xiaotian Wang").first()
        crate.authors.add(author)
        entity = Entity()
        entity.entity_id = "Data Entity of Test Case in %s No.%d"%(discipline,i)
        entity.name = "Data Entity of Test Case in %s No.%d"%(discipline,i)
        entity.type=["File", "ComputationalWorkflow"]
        entity.programmingLanguage = "Common Workflow Language"
        entity.dateCreated = datetime.now()
        entity.dateModified = datetime.now()
        entity.crate = crate
        entity.save()

        print("Add Test Cases Success")