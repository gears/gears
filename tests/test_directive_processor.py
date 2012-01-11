from __future__ import with_statement

import os

from gears.asset_attributes import AssetAttributes
from gears.assets import Asset
from gears.environment import Environment
from gears.exceptions import FileNotFound
from gears.processors import DirectivesProcessor, InvalidDirective

from mock import Mock, patch, sentinel
from unittest2 import TestCase


ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))


class DirectiveProcessorTests(TestCase):

    def setUp(self):
        self.environment = Environment('assets')

    def create_processor(self, path):
        asset_attributes = AssetAttributes(self.environment, path)
        return DirectivesProcessor(asset_attributes)

    @patch('gears.assets.Asset.__init__')
    def test_get_asset(self, init):
        init.return_value = None
        asset = self.create_processor('js/script.js').get_asset(
            sentinel.attributes, sentinel.absolute_path, sentinel.context,
            sentinel.calls)
        init.assert_called_once_with(
            sentinel.attributes, sentinel.absolute_path, sentinel.context,
            sentinel.calls)

    def test_relative_path(self):
        processor = self.create_processor('js/script.js.coffee')
        relative_path = processor.get_relative_path
        self.assertEqual(relative_path('app'), 'js/app.js.coffee')
        self.assertEqual(relative_path('news/app'), 'js/news/app.js.coffee')
        self.assertEqual(relative_path('../admin/app'), 'admin/app.js.coffee')

    def test_find(self):
        with patch.object(self.environment, 'find'):
            self.create_processor('js/script.js.coffee').find('app')
            self.assertEqual(self.environment.find.call_count, 1)

            asset_attributes, logical = self.environment.find.call_args[0]
            self.assertTrue(logical)
            self.assertEqual(asset_attributes.path, 'js/app.js.coffee')
            self.assertIs(asset_attributes.environment, self.environment)

    def test_parse_multiline_comment(self):
        processor = self.create_processor('js/script.js')
        directives = processor.parse_directives('\n'.join((
            '/*',
            ' * =require_self',
            ' *= require header',
            ' * =require body',
            ' * =require "footer"',
            ' */')))
        self.assertEqual(list(directives), [
            (1, ['require_self']),
            (2, ['require', 'header']),
            (3, ['require', 'body']),
            (4, ['require', 'footer'])])

    def test_parse_slash_commend(self):
        processor = self.create_processor('js/script.js')
        directives = processor.parse_directives('\n'.join((
            '//= require "file with whitespaces"',
            '// =require another_file')))
        self.assertEqual(list(directives), [
            (0, ['require', 'file with whitespaces']),
            (1, ['require', 'another_file'])])

    def test_parse_dash_comment(self):
        processor = self.create_processor('js/script.js.coffee')
        directives = processor.parse_directives('\n'.join((
            '#= require models',
            '# =require views')))
        self.assertEqual(list(directives), [
            (0, ['require', 'models']),
            (1, ['require', 'views'])])

    def test_strip_header(self):
        processor = self.create_processor('js/script.js')
        header = processor.strip_header('\n'.join((
            '/*',
            ' * =require_self',
            ' *',
            ' * =require models',
            ' * =require views',
            ' * =require templates',
            ' */',
        )), [1, 3, 4, 5])
        self.assertEqual(header, '/*\n *\n */')

    def test_process_require_self_directive(self):
        body = []
        processor = self.create_processor('js/script.js')
        processor.process_require_self_directive([], 1, body, 'self_body\n')
        self.assertEqual(body, ['self_body'])

    def test_process_require_self_directive_with_args(self):
        processor = self.create_processor('js/script.js')
        with self.assertRaises(InvalidDirective):
            processor.process_require_self_directive(['app'], 1, [], '')

    def test_process_require_directive(self):
        processor = self.create_processor('js/script.js')
        processor.find = Mock(
            return_value=(sentinel.asset_attributes, sentinel.absolute_path))
        processor.get_asset = Mock()
        processor.get_asset.return_value.__str__ = Mock(
            return_value='asset_body\n')

        body = []
        processor.process_require_directive(
            ['app'], 1, body, sentinel.context, sentinel.calls)
        processor.find.assert_called_once_with('app')
        processor.get_asset.assert_called_once_with(
            sentinel.asset_attributes, sentinel.absolute_path,
            sentinel.context, sentinel.calls)
        self.assertEqual(body, ['asset_body'])

    def test_process_require_directive_if_not_found(self):

        def find(require_path):
            raise FileNotFound(require_path)

        processor = self.create_processor('js/script.js')
        processor.find = Mock(side_effect=find)
        with self.assertRaises(InvalidDirective):
            processor.process_require_directive(['app'], 1, [], {}, set())

    def test_process_require_directive_if_invalid_args(self):
        processor = self.create_processor('js/script.js')
        with self.assertRaises(InvalidDirective):
            processor.process_require_directive([], 1, [], {}, set())
        with self.assertRaises(InvalidDirective):
            processor.process_require_directive(
                ['app', 'models'], 1, [], {}, set())

    def test_process_require_directory_directive(self):

        def item(path):
            return AssetAttributes(self.environment, path), os.path.join(ASSETS_DIR, path)

        def list(path, suffix):
            return (item('js/templates/%s.js.handlebars' % name) for name in 'bca')

        def get_asset(asset_attributes, *args):
            return asset_attributes.path

        processor = self.create_processor('js/script.js')
        processor.get_asset = Mock(side_effect=get_asset)
        self.environment.list = Mock(side_effect=list)

        body = []
        processor.process_require_directory_directive(['templates'], 1, body, {}, set())
        self.environment.list.assert_called_once_with('js/templates', ['.js'])
        self.assertEqual(body, ['js/templates/a.js.handlebars',
                                'js/templates/b.js.handlebars',
                                'js/templates/c.js.handlebars'])

    def test_process_directives(self):

        def process_require_directive(args, lineno, body, context, calls):
            body.append('%s.js' % args[0])

        def process_require_self_directive(args, lineno, body, self_body):
            body.append(self_body)

        processor = self.create_processor('js/script.js')
        processor.parse_directives = Mock(return_value=[
            (0, ['require_self']),
            (1, ['require', 'models']),
            (2, ['require', 'views'])])
        processor.process_require_directive = Mock(
            side_effect=process_require_directive)
        processor.process_require_self_directive = Mock(
            side_effect=process_require_self_directive)
        processor.strip_header = Mock(return_value='// stripped header')

        header, body = processor.process_directives(
            sentinel.header, 'self body', sentinel.context, sentinel.calls)
        processor.strip_header.assert_called_once_with(sentinel.header, [0, 1, 2])
        self.assertEqual(header, '// stripped header')
        self.assertEqual(body, 'self body\n\nmodels.js\n\nviews.js')

    def test_process_directives_if_has_no_require_self(self):

        def process_require_directive(args, lineno, body, context, calls):
            body.append('%s.js' % args[0])

        def process_require_self_directive(args, lineno, body, self_body):
            body.append(self_body)

        processor = self.create_processor('js/script.js')
        processor.parse_directives = Mock(return_value=[
            (1, ['require', 'models']),
            (2, ['require', 'views'])])
        processor.process_require_directive = Mock(
            side_effect=process_require_directive)
        processor.process_require_self_directive = Mock(
            side_effect=process_require_self_directive)
        processor.strip_header = Mock()

        header, body = processor.process_directives(
            sentinel.header, 'self body', sentinel.context, sentinel.calls)
        self.assertEqual(body, 'models.js\n\nviews.js\n\nself body')

    def test_process_directives_if_unknown_directive(self):
        processor = self.create_processor('js/script.js')
        processor.parse_directives = Mock(return_value=[(0, ['unknown'])])
        processor.strip_header = Mock()

        header, body = processor.process_directives(
            sentinel.header, 'self body', sentinel.context, sentinel.calls)
        processor.strip_header.assert_called_once_with(sentinel.header, [])
        self.assertEqual(body, 'self body')

    def test_process(self):
        processor = self.create_processor('js/script.js')
        processor.process_directives = Mock(return_value=['header', 'body'])

        source = processor.process(
            '/*\n * =require jquery\n */\nconsole.log("hello world");',
            sentinel.context, sentinel.calls)
        processor.process_directives.assert_called_once_with(
            '/*\n * =require jquery\n */', '\nconsole.log("hello world");',
            sentinel.context, sentinel.calls)
        self.assertEqual(source, 'header\n\nbody\n')

    def test_process_if_no_match(self):
        processor = self.create_processor('js/script.js')
        processor.process_directives = Mock()

        source = processor.process(
            'console.log("hello world");', sentinel.context, sentinel.calls)
        self.assertFalse(processor.process_directives.called)
        self.assertEqual(source, 'console.log("hello world");\n')
