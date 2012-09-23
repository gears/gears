from gears.asset_attributes import AssetAttributes
from gears.compilers import BaseCompiler
from gears.environment import Environment

from mock import Mock
from unittest2 import TestCase


class StylusCompiler(BaseCompiler):

    result_mimetype = 'text/css'

    def __call__(self, asset):
        pass


class CoffeeScriptCompiler(BaseCompiler):

    result_mimetype = 'application/javascript'

    def __call__(self, asset):
        pass


class TemplateCompiler(BaseCompiler):

    def __call__(self, asset):
        pass


class AssetAttributesTests(TestCase):

    def setUp(self):
        self.environment = Environment('assets')
        self.coffee_script_compiler = CoffeeScriptCompiler.as_handler()
        self.stylus_compiler = StylusCompiler.as_handler()
        self.template_compiler = TemplateCompiler.as_handler()

    def create_attributes(self, path):
        return AssetAttributes(self.environment, path)

    def test_extensions(self):

        def check(path, expected_result):
            extensions = self.create_attributes(path).extensions
            self.assertEqual(extensions, expected_result)

        check('js/readme', [])
        check('js/script.js', ['.js'])
        check('js/script.js.coffee', ['.js', '.coffee'])
        check('js/script.coffee', ['.coffee'])
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
        check('js/script.coffee', 'js/script')

        self.environment.mimetypes.register('.js', 'application/javascript')
        check('js/app.min.js.coffee', 'js/app.min')

    def test_logical_path(self):
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)

        def check(path, expected_result):
            logical_path = self.create_attributes(path).logical_path
            self.assertEqual(logical_path, expected_result)

        check('js/script.js', 'js/script.js')
        check('js/script.js.coffee', 'js/script.js')
        check('js/script.coffee', 'js/script.js')
        check('js/script.min.js', 'js/script.min.js')
        check('js/script.min.js.coffee', 'js/script.min.js')
        check('images/logo.png', 'images/logo.png')
        check('file', 'file')

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
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)

        def check(path, expected_result):
            format_extension = self.create_attributes(path).format_extension
            self.assertEqual(format_extension, expected_result)

        check('js/script.js', '.js')
        check('js/script.js.coffee', '.js')
        check('js/jquery.min.js', '.js')
        check('js/app.js.min.coffee', '.js')
        check('css/style.js.css', '.css')
        check('js/script.coffee', None)
        check('readme', None)

    def test_suffix(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)

        def check(path, expected_result):
            suffix = self.create_attributes(path).suffix
            self.assertEqual(suffix, expected_result)

        check('js/script.js', ['.js'])
        check('js/script.js.coffee', ['.js', '.coffee'])
        check('js/script.coffee', ['.coffee'])
        check('js/script.min.js.coffee', ['.js', '.coffee'])
        check('js/script.js.min.coffee', ['.js', '.min', '.coffee'])
        check('readme', [])

    def test_compiler_extensions(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)
        self.environment.compilers.register('.tmpl', self.template_compiler)

        def check(path, expected_result):
            compiler_extensions = self.create_attributes(path).compiler_extensions
            self.assertEqual(compiler_extensions, expected_result)

        check('js/script.js', [])
        check('js/script.js.coffee', ['.coffee'])
        check('js/script.coffee', ['.coffee'])
        check('js/script.js.coffee.tmpl', ['.coffee', '.tmpl'])
        check('js/hot.coffee.js.tmpl', ['.tmpl'])

    def test_compiler_format_extension(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)
        self.environment.compilers.register('.styl', self.stylus_compiler)
        self.environment.compilers.register('.tmpl', self.template_compiler)

        def check(path, expected_result):
            format_extension = self.create_attributes(path).compiler_format_extension
            self.assertEqual(format_extension, expected_result)

        check('js/application.coffee', '.js')
        check('css/application.styl', '.css')
        check('application.tmpl', None)

    def test_compilers(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)
        self.environment.compilers.register('.tmpl', self.template_compiler)

        def check(path, expected_result):
            compilers = self.create_attributes(path).compilers
            self.assertEqual(compilers, expected_result)

        check('js/script.js', [])
        check('js/script.js.coffee', [self.coffee_script_compiler])
        check('js/script.coffee', [self.coffee_script_compiler])
        check('js/script.js.coffee.tmpl', [self.coffee_script_compiler, self.template_compiler])
        check('js/hot.coffee.js.tmpl', [self.template_compiler])

    def test_mimetype(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.coffee', self.coffee_script_compiler)
        self.environment.compilers.register('.styl', self.stylus_compiler)

        def check(path, expected_result):
            mimetype = self.create_attributes(path).mimetype
            self.assertEqual(mimetype, expected_result)

        check('js/script.js', 'application/javascript')
        check('js/script.js.coffee', 'application/javascript')
        check('js/script.coffee', 'application/javascript')
        check('css/style.min.css', 'text/css')
        check('readme.txt', 'application/octet-stream')

    def test_preprocessors(self):
        first_processor = Mock()
        second_processor = Mock()
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.styl', self.stylus_compiler)
        self.environment.preprocessors.register('text/css', first_processor)
        self.environment.preprocessors.register('text/css', second_processor)

        def check(path, expected_result):
            preprocessors = self.create_attributes(path).preprocessors
            self.assertEqual(preprocessors, expected_result)

        check('readme.txt', [])
        check('js/script.js', [])
        check('css/style.css', [first_processor, second_processor])
        check('css/style.css.styl', [first_processor, second_processor])
        check('css/style.styl', [first_processor, second_processor])

    def test_postprocessors(self):
        first_processor = Mock()
        second_processor = Mock()
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.js', 'application/javascript')
        self.environment.compilers.register('.styl', self.stylus_compiler)
        self.environment.postprocessors.register('text/css', first_processor)
        self.environment.postprocessors.register('text/css', second_processor)

        def check(path, expected_result):
            postprocessors = self.create_attributes(path).postprocessors
            self.assertEqual(postprocessors, expected_result)

        check('readme.txt', [])
        check('js/script.js', [])
        check('css/style.css', [first_processor, second_processor])
        check('css/style.css.styl', [first_processor, second_processor])
        check('css/style.styl', [first_processor, second_processor])
