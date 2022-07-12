
from urllib import response
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from .models import Citation, Crate, Organization, Person, Entity
from rocrate.rocrate import ROCrate, Entity as RO_Entity
from .documents import CrateDocument
from elasticsearch_dsl import Q
import urllib.request
from django.contrib import messages
from django.template.loader import render_to_string

# Create your views here.
def portal(request):
    if request.method == 'GET':
        return render(request, 'portal.html')
    search = request.POST.get("search")
    field = request.POST.get("field")
    return redirect("/search?field=%s&q=%s"%(field,search))

def search(request):
    if request.method == 'GET':
        search = request.GET.get('q')
        field = request.GET.get('field')
        if field == "All":
            entry_query = Q("multi_match", query=search, fuzziness="auto", fields=[
                'name',
                'description',
                'license',
                'keywords',
                'identifier',
                'dicipline',
                ])
            entity_query = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.name',
                'entities.type',
                'entities.entity_id',
                'entities.description',
                'entities.programmingLanguage',
                ])))
            author_query = Q("nested", path="authors", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'authors.name',
                'authors.id',
                ])))
            organization_query = Q("nested", path="publisher", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'publisher.name',
                'publisher.id',
                ])))
            citation_query = Q("nested", path="citation", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'citation.name',
                'citation.id',
                ])))
            result = CrateDocument.search().query(entry_query | entity_query | author_query | organization_query | citation_query)
        
        elif field == "Data Entities":
            entity_query = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.name',
                'entities.type',
                'entities.entity_id',
                'entities.description',
                'entities.programmingLanguage',
                ])))
            result = CrateDocument.search().query(entity_query)
        
        elif field == "Person": #TODO: creator, publisher?
            author_query = Q("nested", path="authors", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'authors.name',
                'authors.id',
                ])))
            result = CrateDocument.search().query(author_query)
        elif field == "Publications":
            citation_query = Q("nested", path="citation", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'citation.name',
                'citation.id',
                ])))
            result = CrateDocument.search().query(citation_query)
        elif field == "Organizations":
            organization_query = Q("nested", path="publisher", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'publisher.name',
                'publisher.id',
                ])))
            result = CrateDocument.search().query(organization_query)
        elif field == "Types" or field == "Profiles": #TODO: Profiles
            entity_query = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.type',
                ])))
            result = CrateDocument.search().query(entity_query)
        elif field == "Programming Languages": #TODO: programming language id, altername
            entity_query = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.programmingLanguage',
                ])))
            result = CrateDocument.search().query(entity_query)
        elif field == "Licenses":
            entry_query = Q("multi_match", query=search, fuzziness="auto", fields=[
                'license',
                ])
            result = CrateDocument.search().query(entry_query)
        elif field == "Diciplines":
            entry_query = Q("multi_match", query=search, fuzziness="auto", fields=[
                'dicipline',
                ])
            result = CrateDocument.search().query(entry_query)

        resultSet = result.to_queryset()
        return render(request, 'result.html', {'resultset': resultSet})
    search = request.POST.get("search")
    field = request.POST.get("field")
    return redirect("/search?field=%s&q=%s"%(field,search))


def detail(request, cid):
    crate = Crate.objects.filter(id=cid).first()
    return render(request, 'detail.html', {'crate': crate})

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    url = request.POST.get("register")
    field = request.POST.get("field")
    try:
        file_name, headers = urllib.request.urlretrieve(url)
    except:
        messages.error(request, "Parse Failed: Invalid URL!", extra_tags="alert-danger")
        return redirect("/register")
    else:
        return redirect("/register_metadata?filename=%s&url=%s"%(file_name, url))

def metaregister(request):
    filename = request.GET.get('filename')
    inputURL = request.GET.get('url')
    ro = ROCrate(filename)
    if request.method == 'GET':
        people = Person.objects.all()

        if "url" in ro.root_dataset:
            url = ro.root_dataset['url']
        else:
            url = inputURL

        if isinstance(ro.license, RO_Entity):
            license = ro.license['name']
        else:
            license = ro.license

        authors = []
        if "author" in ro.root_dataset:
            if isinstance(ro.root_dataset['author'], list):
                for author in ro.root_dataset['author']:
                    au, created = Person.objects.get_or_create(id = author['@id'], name = author['name'])
                    au.save()
                    authors.append(au)
            else:
                au, created = Person.objects.get_or_create(id = ro.root_dataset['author']['@id'], name = ro.root_dataset['author']['name'])
                au.save()
                authors.append(au)

        keywords = []
        if ro.keywords:
            keywords = ro.keywords
    
        identifier = []
        if "identifier" in ro.root_dataset:
            if isinstance(ro.root_dataset['identifier'], list):
                for id in ro.root_dataset['identifier']:
                    if isinstance(id, RO_Entity):
                        identifier.append(id['@id'])
                    else:
                        identifier.append(id)
            else:
                identifier.append(ro.root_dataset['identifier'])
    
        dicipline = None
        if "dicipline" in ro.root_dataset:
            dicipline = ro.root_dataset['dicipline']
        
        citation = None
        if "citation" in ro.root_dataset:
            ci, created = Citation.objects.get_or_create(id = ro.root_dataset['citation']['@id'], name = ro.root_dataset['citation']['name'])
            ci.save()
            citation = ci
        
        organizations = Organization.objects.all()
        publisher = ro.publisher

        return render(request, 'register_meta.html',{
            'name': ro.name,
            'url': url,
            'description': ro.description,
            'datePublished': ro.datePublished,
            'license': license,
            'authors': authors,
            'keywords': keywords,
            'identifier': identifier,
            'dicipline': dicipline,
            'people': people,
            'citation': citation,
            'publisher': publisher,
            'organizations': organizations,
        })
    
    #post
    crate = Crate()
    crate.name = request.POST.get('name')
    crate.description = request.POST.get('description')
    crate.datePublished = ro.datePublished
    crate.url = request.POST.get('url')
    crate.license = request.POST.get('license')
    authors = request.POST.getlist("authors[]")
    publisher = request.POST.get('publisher')
    citation_name = request.POST.get('citation_name')
    citation_id = request.POST.get('citation_id')
    crate.keywords = request.POST.getlist("keywords[]")
    crate.identifier = request.POST.getlist('identifier[]')
    crate.dicipline = request.POST.get('dicipline')
    crate.save()
    for au in authors:
        author = Person.objects.filter(id=au).first()
        crate.authors.add(au)
    
    if publisher != "none":
        pub = Organization.objects.filter(id=publisher).first()
        crate.publisher.add(pub)

    if citation_id != None:
        cit, created = Citation.objects.get_or_create(id=citation_id)
        if created:
            cit.name = citation_name
        cit.save()
        crate.citation.add(cit)

    for entity in ro.data_entities:
        de = Entity()
        de.crate = crate
        de.entity_id = entity['@id']
        if "name" in entity:
            de.name = entity['name']
        if "description" in entity:
            de.description = entity['description']
        type = entity['@type']
        if isinstance(type, list):
            de.type = type
        else:
            de.type = [type]
        
        if "dateCreated" in entity:
            de.dateCreated = entity['dateCreated']
        if "dateModified" in entity:
            de.dateModified = entity['dateModified']
        if "programmingLanguage" in entity:
            de.programmingLanguage = entity['programmingLanguage']['name']
        de.save()

    return HttpResponse("save success") #success page

def saveAuthor(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST": #ajax
        id = request.POST.get("author_id")
        name = request.POST.get("author_name")
        authors = request.POST.getlist("authors[]")
        authormodel = []
        for au in authors:
            author = Person.objects.filter(id=au).first()
            authormodel.append(author)
        person, created = Person.objects.get_or_create(id=id)
        if not created:
            return JsonResponse({"error": "Author or ID already exists"}, status=400)
        person.name = name
        person.save()
        people = Person.objects.all()
        html = render_to_string('authors.html', {'people': people, 'authors':authormodel})
        return HttpResponse(html)
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return JsonResponse({"error": ""}, status=400)

def savePublisher(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST": #ajax
        id = request.POST.get("organization_id")
        name = request.POST.get("organization_name")
        org, created = Organization.objects.get_or_create(id=id)
        if not created:
            return JsonResponse({"error": "Organization or ID already exists"}, status=400)
        org.name = name
        org.save()
        orgs = Organization.objects.all()
        html = render_to_string('organization.html', {'organizations': orgs})
        return HttpResponse(html)
    return JsonResponse({"error": ""}, status=400)