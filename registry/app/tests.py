from django.utils import timezone
from django.test import RequestFactory, TestCase
from datetime import date, datetime
from .models import Crate, People, Organization, Entity
from django.contrib.messages.storage.fallback import FallbackStorage

from .views import delete, detail, edit, metaregister, portal, register, saveAuthor, savePublisher, search

# Create your tests here.
class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        discipline = "TEST"
        testauthor = People(ocrid="Test111", name="Xiaotian Wang")
        testauthor.save()
        People(ocrid="https://orcid.org/test", name="test").save()
        for i in range(1,10):
            crate = Crate()
            crate.name = "Test Case in %s No.%d"%(discipline,i)
            crate.description = "Test Case in %s No.%d"%(discipline,i)
            crate.datePublished = timezone.now()
            crate.license = "Apache-2.0"
            crate.keywords = ["test","%s"%discipline]
            crate.discipline = ["%s"%discipline]
            crate.profile = "Workflow RO-Crate Profile"
            crate.profileID = "https://about.workflowhub.eu/Workflow-RO-Crate/"
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
            entity.dateCreated = timezone.now()
            entity.dateModified = timezone.now()
            entity.crate = crate
            entity.save()
        # self.user = User.objects.create_user(
        #     username='jacob', email='jacob@…', password='top_secret')

    def test_portal(self):
        # Create an instance of a GET request.
        request = self.factory.get('/')
        # request.user = self.user
        response = portal(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)

    def test_portal_post(self):
        request = self.factory.post('/', {'search':'workflow','field':'All'}, follow=True)
        response = portal(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)
    
    def search_with_field(self, field):
        # Create an instance of a GET request.
        request = self.factory.get('/search?field=%s&q=workflow&sort=Relevance&startDate=&endDate=&createdStartDate=&createdEndDate=&modifiedStartDate=&modifiedEndDate'%field)
        # request.user = self.user
        response = search(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_search_fields(self):
        self.search_with_field("All")
        self.search_with_field("Data Entities")
        self.search_with_field("Person")
        self.search_with_field("Publications")
        self.search_with_field("Organizations")
        self.search_with_field("Types")
        self.search_with_field("Programming Languages")
        self.search_with_field("Licenses")
        self.search_with_field("Profiles")
        self.search_with_field("Disciplines")
        self.search_with_field("Related")

    def test_search_filters(self):
        # Create an instance of a GET request.
        request = self.factory.get('/search?field=All&q=workflow&sort=Date&startDate=2022-08-05&endDate=2022-08-07&createdStartDate=2022-08-02&createdEndDate=2022-08-07&modifiedStartDate=2022-08-05&modifiedEndDate=2022-08-07')
        # request.user = self.user
        response = search(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_search_sort_title(self):
        # Create an instance of a GET request.
        request = self.factory.get('/search?field=All&q=workflow&sort=Title&startDate=2022-08-05&endDate=2022-08-07&createdStartDate=2022-08-02&createdEndDate=2022-08-07&modifiedStartDate=2022-08-05&modifiedEndDate=2022-08-07')
        # request.user = self.user
        response = search(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)

    def test_search_post(self):
        request = self.factory.post('/search', {'search':'workflow','field':'All'}, follow=True)
        response = search(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)
    
    def test_detail(self):
        self.createTestCrate(333)
        request = self.factory.get('/crate/333/')
        # request.user = self.user
        response = detail(request, 333)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_register(self):
        request = self.factory.get('/register')
        # request.user = self.user
        response = register(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_register_post(self):
        request = self.factory.post('/register',  {'url':'https://workflowhub.eu/workflows/372/ro_crate?version=1','field':'All'}, follow=True)
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        # request.user = self.user
        response = register(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)
    
    def test_metadata(self):
        request = self.factory.get('/register_metadata?filename=%s&url=%s'%("test/workflow-test-1.crate.zip", "https://workflowhub.eu/workflows/372/ro_crate?version=1"))
        # request.user = self.user
        response = metaregister(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_metadata_2(self):
        request = self.factory.get('/register_metadata?filename=%s&url=%s'%("test/workflow-test-2.crate", "https://workflowhub.eu/workflows/372/ro_crate?version=1"))
        # request.user = self.user
        response = metaregister(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_metadata_alreadyexists(self):
        crate = self.createTestCrate(688)
        crate.identifier = ["https://workflowhub.eu/workflows/372?version=1"]
        crate.save()
        
        request = self.factory.get('/register_metadata?filename=%s&url=%s'%("test/workflow-test-2.crate", "https://workflowhub.eu/workflows/372/ro_crate?version=1"))
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = metaregister(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)

    def test_metadata_post(self):
        request = self.factory.post('/register_metadata?filename=%s&url=%s'%("test/workflow-test-1.crate.zip", "https://workflowhub.eu/workflows/372/ro_crate?version=1"),
          {
            'name':'TestName',
            'description':'test',
            'url':'https://workflowhub.eu/workflows/372/ro_crate?version=1',
            'license': 'a',
            'authors[]': ['Test111|Xiaotian Wang'],
            'publisher': "none",
            'identifier': ['https://workflowhub.eu/workflows/372?version=1']
            }, follow=True)

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = metaregister(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)
    
    def test_saveAuthor(self):
        request = self.factory.post('/save_author', {'author_id':'test222', 'author_name':'test', 'authors[]':['Test111']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # request.user = self.user
        response = saveAuthor(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_saveAuthor_not_ajax(self):
        request = self.factory.post('/save_author', {'author_id':'test222', 'author_name':'test', 'authors[]':['Test111']})
        # request.user = self.user
        response = saveAuthor(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 400)
    
    def test_savePublisher(self):
        request = self.factory.post('/save_publisher', {'organization_id':'test222', 'organization_name':'test'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # request.user = self.user
        response = savePublisher(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_savePublisher_not_ajax(self):
        request = self.factory.post('/save_publisher', {'organization_id':'test222', 'organization_name':'test'})
        # request.user = self.user
        response = savePublisher(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 400)
    
    def test_edit(self):
        self.createTestCrate(888)
        request = self.factory.get('/crate/888/edit')
        # request.user = self.user
        response = edit(request, 888)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)
    
    def test_edit_post(self):
        self.createTestCrate(888)
        request = self.factory.post('/crate/888/edit',
          {
            'name':'TestName',
            'description':'test',
            'url':'https://workflowhub.eu/workflows/372/ro_crate?version=1',
            'license': 'a',
            'authors[]': ['Test111|Xiaotian Wang'],
            'publisher': "none",
            'identifier': ['https://workflowhub.eu/workflows/372?version=1']
            }, follow=True)

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = edit(request, 888)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)
    
    def test_delete(self):
        self.createTestCrate(888)
        request = self.factory.get('/crate/888/delete')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        # request.user = self.user
        response = delete(request, 888)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 302)

    def createTestCrate(self, i):
        discipline = "test"
        crate = Crate()
        crate.id = i
        crate.name = "Test Case in %s No.%d"%(discipline,i)
        crate.description = "Test Case in %s No.%d"%(discipline,i)
        crate.datePublished = timezone.now()
        crate.license = "Apache-2.0"
        crate.keywords = ["test","%s"%discipline]
        crate.discipline = ["%s"%discipline]
        crate.profile = "Workflow RO-Crate Profile"
        crate.profileID = "https://about.workflowhub.eu/Workflow-RO-Crate/"
        crate.url="#TestcaseIn%sNo%d"%(discipline, i)
        crate.identifier = ["#TestcaseIn%sNo%d"%(discipline, i)]
        crate.save()
        author = People.objects.filter(ocrid="Test111", name="Xiaotian Wang").first()
        author2 = People.objects.filter(name="test").first()
        crate.authors.add(author)
        crate.authors.add(author2)
        entity = Entity()
        entity.entity_id = "Data Entity of Test Case in %s No.%d"%(discipline,i)
        entity.name = "Data Entity of Test Case in %s No.%d"%(discipline,i)
        entity.type=["File", "ComputationalWorkflow"]
        entity.programmingLanguage = "Common Workflow Language"
        entity.dateCreated = timezone.now()
        entity.dateModified = timezone.now()
        entity.crate = crate
        entity.save()

        return crate