from datetime import datetime, date
from urllib import response, parse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from .models import Citation, Crate, Organization, People, Entity
from rocrate.rocrate import ROCrate, Entity as RO_Entity
from .documents import CrateDocument
from elasticsearch_dsl.query import MoreLikeThis
from elasticsearch_dsl import Q, Search
import urllib.request
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from app.facet import CrateSearch
from django.db.models import Case, When
from django.db.models.fields import IntegerField
import validators

# Create your views here.
def portal(request):
    if request.method == 'GET':
        return render(request, 'portal.html')
    search = request.POST.get("search")
    field = request.POST.get("field")
    return redirect("/search?field=%s&q=%s&sort=Relevance"%(parse.quote_plus(field),parse.quote_plus(search)))

def search(request):
    if request.method == 'GET':
        search = request.GET.get('q')
        field = request.GET.get('field')
        disciplines = request.GET.getlist('discipline')
        licenses = request.GET.getlist('license')
        types = request.GET.getlist('type')
        programs = request.GET.getlist('pro')
        startDate = request.GET.get('startDate')
        endDate = request.GET.get('endDate')
        createdStartDate = request.GET.get('createdStartDate')
        createdEndDate = request.GET.get('createdEndDate')
        modifiedStartDate = request.GET.get('modifiedStartDate')
        modifiedEndDate = request.GET.get('modifiedEndDate')
        
        filter = {"discipline":disciplines, "license":licenses, "type":types, "programmingLanguage":programs}
        if field == "All":
            entry_query = Q("multi_match", query=search, fuzziness="auto", fields=[
                'name',
                'description',
                'license',
                'keywords',
                'identifier',
                'discipline',
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
                'authors.ocrid',
                ])))
            organization_query = Q("nested", path="publisher", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'publisher.name',
                'publisher.id',
                ])))
            citation_query = Q("nested", path="citation", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'citation.name',
                'citation.id',
                ])))
            q = entry_query | entity_query | author_query | organization_query | citation_query
            # result = CrateDocument.search().query(entry_query | entity_query | author_query | organization_query | citation_query)

        elif field == "Data Entities":
            q = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.name',
                'entities.type',
                'entities.entity_id',
                'entities.description',
                'entities.programmingLanguage',
                ])))
        
        elif field == "Person": #TODO: creator, publisher?
            q = Q("nested", path="authors", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'authors.name',
                'authors.ocrid',
                ])))
            
        elif field == "Publications":
            q = Q("nested", path="citation", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'citation.name',
                'citation.id',
                ])))
            
        elif field == "Organizations":
            q = Q("nested", path="publisher", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'publisher.name',
                'publisher.id',
                ])))
            
        elif field == "Types" or field == "Profiles": #TODO: Profiles
            q = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.type',
                ])))
            
        elif field == "Programming Languages": #TODO: programming language id, altername
            q = Q("nested", path="entities", query=(Q("multi_match", query=search, fuzziness="auto", fields=[
                'entities.programmingLanguage',
                ])))
            
        elif field == "Licenses":
            q = Q("multi_match", query=search, fuzziness="auto", fields=[
                'license',
                ])
            
        elif field == "Disciplines":
            q = Q("multi_match", query=search, fuzziness="auto", fields=[
                'discipline',
                ])
        elif field == "Related":
            q = Q("more_like_this", fields=[
                'name',
                'keywords',
                'discipline',
                'license',
                'authors',
                ], like=[
                    {
                        "_index": "crates",
                        "_id": search,
                    }
                ], min_term_freq=1, minimum_should_match=5)

        datefilter = {}
        if startDate not in ("","undefined",None):
            datefilter["gte"] = startDate
        if endDate not in ("","undefined",None):
            datefilter["lte"] = endDate

        createdfilter = {}
        if createdStartDate not in ("","undefined",None):
            createdfilter["gte"] = createdStartDate
        if createdEndDate not in ("","undefined",None):
            createdfilter["lte"] = createdEndDate

        modifiedfilter = {}
        if modifiedStartDate not in ("","undefined",None):
            modifiedfilter["gte"] = modifiedStartDate
        if modifiedEndDate not in ("","undefined",None):
            modifiedfilter["lte"] = modifiedEndDate
        crate_search = CrateSearch("", filters=filter, q=q, datefilter=datefilter, created=createdfilter, modified=modifiedfilter)
            
        response = crate_search.execute()
        resultSet = to_queryset(response) 
        sort = request.GET.get('sort')
        if sort == "Date":
            resultSet = resultSet.order_by('datePublished')
        elif sort == "Title":
            resultSet = resultSet.order_by('name')
        paginator = Paginator(resultSet, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'result.html', {
            'resultset': page_obj, 
            'discipline':response.facets.discipline, 
            'license':response.facets.license,
            'type': response.facets.type,
            'programming': response.facets.programmingLanguage,
            })
    search = request.POST.get("search")
    field = request.POST.get("field")
    return redirect("/search?field=%s&q=%s&sort=Relevance"%(parse.quote_plus(field),parse.quote_plus(search)))


def detail(request, cid):
    crate = Crate.objects.filter(id=cid).first()
    # s = Search()
    # s = s.query(MoreLikeThis(like={"_index": "crates", "_id": cid}, fields=[
    #     'name',
    #     'description',
    #     'keywords',
    #     'discipline',
    #     'license',
    #     'identifier',
    #     ]))
    # print(s.execute().to_dict())
    related_query = Q("more_like_this", fields=[
        'name',
        'keywords',
        'discipline',
        'license',
        'authors',
        ], like=[
            {
                "_index": "crates",
                "_id": str(cid),
            }
        ], min_term_freq=1, minimum_should_match=5)
    result = CrateDocument.search().query(related_query)
    resultSet = result.to_queryset()
    authors = crate.authors.all()
    authorlist = []
    for author in authors:
        au = {}
        au['author'] = author
        if validators.url(author.ocrid):
            au['isocr'] = True
        else:
            au['isocr'] = False
        authorlist.append(au)
    return render(request, 'detail.html', {'crate': crate, 'related': resultSet, 'authorlist':authorlist})

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
        people = People.objects.all()

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
                    au, created = People.objects.get_or_create(ocrid = author['@id'], name = author['name'])
                    au.save()
                    authors.append(au)
            else:
                au, created = People.objects.get_or_create(ocrid = ro.root_dataset['author']['@id'], name = ro.root_dataset['author']['name'])
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
        
        #if exists:
        for id in identifier:
            res = Crate.objects.filter(identifier__contains=[id])
            if len(res) != 0:
                messages.warning(request, "RO-Crate already exists!", extra_tags="alert-warning")
                return redirect("/crate/%s/"%res.first().id)
        
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
            'people': people,
            'citation': citation,
            'publisher': publisher,
            'organizations': organizations,
            'mode': "Rsegister",
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
    crate.discipline = request.POST.getlist('discipline[]')
    crate.save()
    for au in authors:
        aulist = au.split("|")
        author = People.objects.filter(ocrid=aulist[0], name=aulist[1]).first()
        crate.authors.add(author)
    
    if publisher != "none":
        pub = Organization.objects.filter(id=publisher).first()
        crate.publisher.add(pub)

    if citation_id != None and citation_id !="":
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

    messages.success(request, "Register Successed!", extra_tags="alert-success")
    return redirect('/crate/%s'%crate.id)

def saveAuthor(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST": #ajax
        id = request.POST.get("author_id")
        name = request.POST.get("author_name")
        authors = request.POST.getlist("authors[]")
        authormodel = []
        for au in authors:
            author = People.objects.filter(ocrid=au).first()
            authormodel.append(author)
        person, created = People.objects.get_or_create(ocrid=id, name=name)
        if not created:
            return JsonResponse({"error": "Author or ID already exists"}, status=400)
        person.save()
        people = People.objects.all()
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

def to_queryset(response):
    pks = [result.meta.id for result in response]

    qs = Crate.objects.filter(pk__in=pks)

    preserved_order = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(pks)],
        output_field=IntegerField()
    )
    qs = qs.order_by(preserved_order)
    return qs


def edit(request, cid):
    crate = Crate.objects.filter(id=cid).first()
    people = People.objects.all()
    organizations = Organization.objects.all()
    if request.method == 'GET':
        return render(request, 'register_meta.html',{
                'id': cid,
                'name': crate.name,
                'url': crate.url,
                'description': crate.description,
                'datePublished': crate.datePublished,
                'license': crate.license,
                'authors': crate.authors.all(),
                'keywords': crate.keywords,
                'identifier': crate.identifier,
                'people': people,
                'citation': crate.citation,
                'publisher': crate.publisher,
                'organizations': organizations,
                'mode': "Edit",
            })

    crate.description = request.POST.get('description')
    crate.license = request.POST.get('license')
    authors = request.POST.getlist("authors[]")
    publisher = request.POST.get('publisher')
    citation_name = request.POST.get('citation_name')
    citation_id = request.POST.get('citation_id')
    crate.keywords = request.POST.getlist("keywords[]")
    crate.identifier = request.POST.getlist('identifier[]')
    crate.discipline = request.POST.getlist('discipline[]')
    crate.save()
    crate.authors.clear()
    for au in authors:
        aulist = au.split("|")
        author = People.objects.filter(ocrid=aulist[0], name=aulist[1]).first()
        if not crate.authors.filter(ocrid=aulist[0], name=aulist[1]).exists():
            crate.authors.add(author)
    
    if publisher != "none":
        pub = Organization.objects.filter(id=publisher).first()
        if not crate.publisher.filter(id=publisher).exists():
            crate.publisher.add(pub)

    if citation_id != None and citation_id !="":
        cit, created = Citation.objects.get_or_create(id=citation_id)
        if created:
            cit.name = citation_name
        cit.save()
        if not crate.citation.filter(id=citation_id):
            crate.citation.add(cit)
    
    messages.success(request, "Edit Successed!", extra_tags="alert-success")
    return redirect('/crate/%s'%crate.id)
    
def delete(request, cid):
    crate = Crate.objects.filter(id=cid).first()
    crate.delete()
    messages.success(request, "Delete Successed!", extra_tags="alert-success")
    return redirect('/')