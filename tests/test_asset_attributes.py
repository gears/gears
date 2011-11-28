from gears.asset_attributes import AssetAttributes
from gears.environment import Environment

from mock import Mock
from unittest2 import TestCase


class AssetAttributesTests(TestCase):

    def setUp(self):
        self.environment = Environment('assets')

    def create_attributes(self, path):
        return AssetAttributes(self.environment, path)

    def test_extensions(self):

        def check(path, expected_result):
            extensions = self.create_attributes(path).extensions
            self.assertEqual(extensions, expected_result)

        check('js/readme', [])
        check('js/script.js', ['.js'])
        check('js/script.js.coffee', ['.js', '.coffee'])
        check('js/app.min.js.coffee', ['.min', '.js', '.coffee'])
        check('js/.htaccess', ['.htaccess'])

    def test_path_without_suffix(self):

        def check(path, expected_result):
            attributes = self.create_attributes(path)
            path_without_suffix = attributes.path_without_suffix
            self.assertEqual(path_without_suffix, expected_result)

        check('js/.htaccess', 'js/')
        check('js/readme', 'js/readme')
        check('js/app.min.js.coffee', 'js/app')

        self.environment.mimetypes.register('.js', 'application/javascript')
        check('js/app.min.js.coffee', 'js/app.min')

    def test_search_paths(self):
        self.environment.mimetypes.register('.js', 'application/javascript')

        def check(path, expected_result):
            search_paths = self.create_attributes(path).search_paths
            self.assertEqual(search_paths, expected_result)

        check('js/script.js', ['js/script.js', 'js/script/index.js'])
        check('js/app.min.js', ['js/app.min.js', 'js/app.min/index.js'])
        check('js/.htaccess', ['js/.htaccess', 'js/index.htaccess'])
        check('js/index.js', ['js/index.js'])

    def test_format_extension(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.engines.register('.coffee', Mock())

        def check(path, expected_result):
            format_extension = self.create_attributes(path).format_extension
            self.assertEqual(format_extension, expected_result)

        check('js/script.js', '.js')
        check('js/script.js.coffee', '.js')
        check('js/jquery.min.js', '.js')
        check('js/app.js.min.coffee', '.js')
        check('css/style.js.css', '.css')
        check('readme', None)

    def test_suffix(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.engines.register('.coffee', Mock())

        def check(path, expected_result):
            suffix = self.create_attributes(path).suffix
            self.assertEqual(suffix, expected_result)

        check('js/script.js', ['.js'])
        check('js/script.js.coffee', ['.js', '.coffee'])
        check('js/script.min.js.coffee', ['.js', '.coffee'])
        check('js/script.js.min.coffee', ['.js', '.min', '.coffee'])
        check('readme', [])

    def test_engine_extensions(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.engines.register('.coffee', Mock())
        self.environment.engines.register('.tmpl', Mock())

        def check(path, expected_result):
            engine_extensions = self.create_attributes(path).engine_extensions
            self.assertEqual(engine_extensions, expected_result)

        check('js/script.js', [])
        check('js/script.js.coffee', ['.coffee'])
        check('js/script.js.coffee.tmpl', ['.coffee', '.tmpl'])
        check('js/hot.coffee.js.tmpl', ['.tmpl'])

    def test_engines(self):
        coffee_engine = Mock()
        template_engine = Mock()
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.engines.register('.coffee', coffee_engine)
        self.environment.engines.register('.tmpl', template_engine)

        def check(path, expected_result):
            engines = self.create_attributes(path).engines
            self.assertEqual(engines, expected_result)

        check('js/script.js', [])
        check('js/script.js.coffee', [coffee_engine])
        check('js/script.js.coffee.tmpl', [coffee_engine, template_engine])
        check('js/hot.coffee.js.tmpl', [template_engine])

    def test_mimetype(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.engines.register('.coffee', Mock())
        self.environment.engines.register('.styl', Mock())

        def check(path, expected_result):
            mimetype = self.create_attributes(path).mimetype
            self.assertEqual(mimetype, expected_result)

        check('js/script.js', 'application/javascript')
        check('js/script.js.coffee', 'application/javascript')
        check('css/style.min.css', 'text/css')
        check('readme.txt', 'application/octet-stream')

    def test_preprocessors(self):
        first_processor = Mock()
        second_processor = Mock()
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        preprocessors = self.environment.preprocessors
        preprocessors.register('text/css', Mock(return_value=first_processor))
        preprocessors.register('text/css', Mock(return_value=second_processor))

        def check(path, expected_result):
            preprocessors = self.create_attributes(path).preprocessors
            self.assertEqual(preprocessors, expected_result)

        check('readme.txt', [])
        check('js/script.js', [])
        check('css/style.css', [first_processor, second_processor])

    def test_postprocessors(self):
        first_processor = Mock()
        second_processor = Mock()
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        postprocessors = self.environment.postprocessors
        postprocessors.register('text/css', Mock(return_value=first_processor))
        postprocessors.register('text/css', Mock(return_value=second_processor))

        def check(path, expected_result):
            postprocessors = self.create_attributes(path).postprocessors
            self.assertEqual(postprocessors, expected_result)

        check('readme.txt', [])
        check('js/script.js', [])
        check('css/style.css', [first_processor, second_processor])

    def test_processors(self):
        preprocessor = Mock()
        postprocessor = Mock()
        coffee_engine = Mock()
        template_engine = Mock()
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.preprocessors.register(
            'application/javascript', Mock(return_value=preprocessor))
        self.environment.postprocessors.register(
            'application/javascript', Mock(return_value=postprocessor))
        self.environment.engines.register('.coffee', coffee_engine)
        self.environment.engines.register('.tmpl', template_engine)

        self.assertEqual(
            self.create_attributes('js/script.js.coffee.tmpl').processors,
            [preprocessor, template_engine, coffee_engine, postprocessor])
