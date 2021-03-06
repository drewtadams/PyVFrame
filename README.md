# PyVFrame
Framework built in Python3 for easy vanilla web development

## Installation
From github:
```bash
git clone https://github.com/drewtadams/PyVFrame.git
```

With bash:

Add the following to your `bash_rc` or `bash_profile`:
```bash
function pyvframe () {
    # check if a param was passed
    if [ $# -gt 0 ]
    then
        if [ $1 == 'init' ]
        then
            python3 pyvframe.py init
        elif [ $1 == 'build' ]
        then
            python3 pyvframe.py build
        elif [ $1 == 'watch' ]
        then
            python3 pyvframe.py watch
        else
            echo $'\nInvalid parameters. Should be: pyvframe [ init | build | watch ]'
        fi
    else
        # check if a project already exists
        if [ -d "PyVFrame" ] || [ -f "pyvframe.py" ]
        then
            echo $'\nProject already exists here. Did you mean to use \033[1;35mpyvframe init\033[0m or \033[1;35mpyvframe build\033[0m?\n'
        else
            # verify the user wants to create a new project
            read -p $'\nDo you want to create a new project here? [y/n] : ' user_response

            if [ $user_response == 'Y' ] || [ $user_response == 'y' ]
            then
                echo $'\n'
                git clone https://github.com/drewtadams/PyVFrame.git
                echo $'\n'
                cd PyVFrame
            fi
        fi
    fi
}
```

Then run `pyvframe` from where you want the repo cloned. Once the repo is cloned, you can also initialize or build your project by running `pyvframe init` and `pyvframe build` from your project's root directory. Once you have a project initialized, you can also run `pyvframe build`

## Usage
To initialize a new project from your project root:
```bash
python pyframe.py init
```

To build an existing project from your project root:
```bash
python pyframe.py build
```

### Default File Structure
```
root
 - build
   - assets
     - css
       - vendor
       - main.css
     - images
     - js
       - vendor
       - main.js
     - scss
       - main.scss
   - components
   - content
   - pages
     - index.html

 - dist
   - assets
     - css
       - vendor
       - main.css
     - images
     - js
       - vendor
       - main.js
     - index.html
```

### Making a Page
There are currently 4 primary building blocks in PyVFrame:

1. Injection points
2. Content blocks
3. Components
4. Pages

---

Injection points allow you to inject custom inline python (3.0+) or meta data from the `settings.json` file. To use these injection points, you need to wrap your python code in double curly braces (`{{` and `}}`) and your meta data in double square brackets (`[[` and `]]`). Injections can be used anywhere throughout components and/or pages, including element property values. See below:

```html
<title>[[ page_meta.title ]]</title>
...
<div>the sum of 4 + 4 + 4 is {{ sum([4,4,4]) }}</div>
```

Dot notation is used to access data from `settings.json` and almost always follows a standard traversal (e.g. if you look at `settings.json` to get the default title, you would normally use `page_meta.default.title`), but shortcuts are used specifically when dealing with page meta data to allow for more dynamic usage. When dealing with `page_meta` in `settings.json`, the values stored in `default` are used for every page not specified below it.

One important note with injection points is that it is possible to nest meta tags (`[[` and `]]`) inside of code tags `{{` and `}}`), but not the other way around due to the rendering order.

---

Content blocks are used in conjunction with a parent component. Content blocks are separate `json` files that are often used for the same components but with different information. For example, if you need 3 FAQ components but with different questions and answers, you could use content blocks. An example of what 2 different blocks look like is below:

```
// demo1.json
{
    "title": "some title",
    "subtitle": "some subtitle",
    "body": "lorem ipsum or somthing"
}

// demo2.json
{
    "title": "demo2 title",
    "subtitle": "demo2 subtitle",
    "body": "demo2 lorem ipsum or somthing"
}
```

To use the data from a content block, the component needs to implement double parenthesis (`((` and `))`) with the key of the value you want to use. A component using the above content blocks might look like this:
```html
<!-- content_demo.html -->
<div>
    <h1>(( title ))</h1>
    <h3>(( subtitle ))</h3>
    <p>(( body ))</p>
    <p>(( title )): (( subtitle ))</p>
</div>
```

To use a component utilizing content blocks, you would do something like this:
```html
<pfcomponent name="content_demo" content="demo1" />
<pfcomponent name="content_demo" content="demo2" />
```

For these particular components, the component name is `content_demo` (from `content_demo.html`) and the content blocks are `demo1` and `demo2` respectively (from `demo1.json` and `demo2.json`, also respectively). Though this will be discussed in the component section, it's important to note that neither propert, the name nor the content value, have file extensions. This `name` is the name of the file of the component **WITHOUT** the file extension (in this case `.html`)

---

Components in their simplest form are just sections of HTML that are often repeated, such as FAQ sections, headers, footers, menus, etc., and are implemented using the custom `<pfcomponent/>` tag. The code for each component is stored in its own separate file. Below is an example of a basic `head` component:

```html
<!-- head.html -->
<head>
    <meta charset="utf-8">

    <title>[[ page_meta.title ]]</title>
    <meta name="description" content="[[ page_meta.description ]]">
    <meta name="author" content="[[ page_meta.author ]]">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="assets/css/main.css">
</head>
```

In the above example, the title, description, and author are being pulled from `settings.json` via injection. This can be used as follows:
```html
<pfcomponent name="head" />
```

All components require certain properties when rendered. A component with just the `name` property will be rendered as a generic component (i.e. content blocks won't render - instead, you'll see `(( block_name ))`). As previously described, components utilizing content blocks require both the `name` and `content` properties. A full list of available components and their requirements can be found at the end.

---

Pages are your standard HTML pages, but with components and injection mixed in. Below is a sample `index.html` file:
```html
<!doctype html>

<html lang="en">
    <pfcomponent name="head" />

    <body>
        <pfcomponent name="header" />

        <div>the product of 4 x 4: {{ 4*4 }}</div>

        <pfcomponent name="content_demo" content="demo1" />

        <hr>

        <pfcomponent pfFor="demo_children" id="myID" class="foobar" />

        <pfcomponent name="footer" />
    </body>
</html>
```

### Components
Generic component:
* required attributes:
  * `name`
```html
<pfcomponent name="[component_name]" />
```

Content block component:
* required attributes:
  * `name`
  * `content`
```html
<pfcomponent name="[component_name]" content="[content_block_name]" />
```
```json
{
    "some_key": "some value"
}
```

Looping component:
* all properties attachable to a div are optional
* the html component template and the json content MUST have the same name as the `pfFor` value (e.g. with `pfFor="faq"`, then you MUST have a file named `faq.json` in the content directory and a file named `faq.html` in the component directory)
* required attributes:
  * `pfFor`
```html
<pfcomponent pfFor="[content_name]" />
```
```
<p>data: (( some_key ))</p>
```
```json
{
    "children": [
        {
            "some_key": "some value 1"
        },
        {
            "some_key": "some value 2"
        }
    ]
}
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
MIT License

Copyright (c) 2020 Drew Adams

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.