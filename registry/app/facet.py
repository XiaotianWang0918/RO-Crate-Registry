from dataclasses import field
from elasticsearch_dsl import FacetedSearch, NestedFacet, TermsFacet, FacetedResponse
from app.documents import CrateDocument


class CrateSearch(FacetedSearch):
    index = 'crates'
    doc_types = [CrateDocument]
    # fields = ['title^5', 'category', 'description', 'body']

    facets = {
        'discipline': TermsFacet(field='discipline'),
        'license': TermsFacet(field='license'),
        'type': NestedFacet("entities", TermsFacet(field='entities.type')),
        'programmingLanguage': NestedFacet("entities", TermsFacet(field='entities.programmingLanguage')),
    }
    def __init__(self, query=None, filters={}, sort=(), q=None, datefilter={}):
        self._q = q
        self._datefilter = datefilter
        super().__init__(query, filters, sort)

    def search(self):
        ' Override search to add your own filters '
        # s = super(BlogSearch, self).search()
        s = CrateDocument.search()
        if self._datefilter != {}:
            s = s.filter("range", datePublished=self._datefilter)
        # return s.filter('term', published=True)
        return s.response_class(FacetedResponse)
    
    def query(self, search, query):
        return search.query(self._q)
