About
=====

The Problem
-----------

The amount of code on the client side significantly grows in the modern
web-applications. JavaScript and CSS files size increases, and it becomes more
difficult to navigate through them. Static files must be broken down into
modules. But the more static files you connect to the HTML page, the more HTTP
requests must be done to load this page, which increases the load time.

CSS and JavaScript files must be combined in production to reduce the number
of subsequent HTTP requests to load the page. This is what Gears does for you.

Motivation and Design Decisions
-------------------------------

But this problem is not new, and there are many awesome Python libraries here
to solve it. So why another one? I've tried almost every existent library, and
none of them fits my needs (and taste). Some of them are only for Django,
some require you to specify asset dependencies in Python (or YAML, or JSON,
or HTML).

So, when I decided to create Gears, I pursued two goals:

- this library should be framework-agnostic and cover as much as possible
  contexts;
- asset dependencies should be described in the usual way, much like this is
  done in the modern languages (e.g., in Python).

Let's look at both.

Usage Contexts
^^^^^^^^^^^^^^

I have to work with static in different contexts:

- in Django projects;
- in reusable Django apps;
- in Flask apps;
- in static sites.

And I want to use only one library for all this contexts (I don't want to deal
with many different libraries).

Asset Dependencies
^^^^^^^^^^^^^^^^^^

Yes, there are already Python libraries, that cover all this contexts. But I
don't like their approach to describing dependencies between assets. It should
be more like how we import modules in Python, Ruby, Java, etc. Dependencies
for the asset should be described in this asset, not in the other place.
Imagine for a moment that all imports in Python project would have to be
described in JSON file in the root of this project. It would be terrible.

I like how this problem is solved in Ruby's Sprockets library. Dependencies
between assets must be described in header comments with special syntax. It was
decided to use this approach and syntax in Gears.
