
import os
import unittest
import tempfile
import notesApp


class notesAppTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, notesApp.app.config['DATABASE'] = tempfile.mkstemp()
        notesApp.app.config['TESTING'] = True
        self.app = notesApp.app.test_client()
        notesApp.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(notesApp.DATABASE)

    def test_addtodb(self):
        self.app.post('/addtodb', data={'title': 'anytitle', 'content': 'anycontent', 'added': 'anydate'})
        self.app.post('/addtodb', data={'title': 338374, 'content': 342423424, 'added': 'anydate'})

    def test_home(self):
        result = self.app.get('/')
        html = result.data.decode()
        assert "Add your note" in html

    def test_results(self):
        result = self.app.get('/results')

    def test_edit(self):
        self.app.post('/edit',
                      data={'title': 'anytitle', 'content': 'anycontent', 'added': 'anydate', 'modified': 'anydate'})
        self.app.post('/edit', data={'title': 2331231, 'content': 'anycontent', 'added': 213313})

    def test_delete(self):
        result = self.app.get('/delete')


    def test_details(self):
        result = self.app.get('/details')

    def test_readonly(self):
        result = self.app.get('/readonly')


if __name__ == '__main__':
    unittest.main()
