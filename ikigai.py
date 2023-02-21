#!/usr/bin/env python3 -u
# -*- mode: python; coding: utf-8 -*-
# pylint: disable=no-member
"""
Ikigai is a Japanese concept that means "a reason for being".

The word refers to having a meaningful direction or purpose in life,
constituting the sense of one's life being made worthwhile,
with actions taken towards achieving one's Ikigai resulting
in satisfaction and a sense of meaning to life.
"""
from flask import Flask
from flask.templating import render_template_string
from easybase import get
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.callbacks import CustomJS

app = Flask(__name__)


@app.route('/')
def index():
    """Index."""
    controls = {
        'reviews': Slider(title='Min # of reviews', value=10, start=10, end=200000, step=10),
        'min_year': Slider(title='Start Year', start=1970, end=2021, value=1970, step=1),
        'max_year': Slider(title='End Year', start=1970, end=2021, value=2021, step=1),
        'genre': Select(title='Genre', value='All', options=['All', 'Comedy', 'Sci-Fi', 'Action',
                                                             'Drama', 'War', 'Crime', 'Romance',
                                                             'Thriller', 'Music', 'Adventure',
                                                             'History', 'Fantasy', 'Documentary',
                                                             'Horror', 'Mystery', 'Family',
                                                             'Animation', 'Biography', 'Sport',
                                                             'Western', 'Short', 'Musical'])
    }

    controls_array = controls.values()

    def selected_movies():
        return get('Dt-p-a0jVTBSVQji', 0, 2000, 'password')

    source = ColumnDataSource()

    callback = CustomJS(args=dict(source=source, controls=controls), code="""
        if (!window.full_data_save) {
            window.full_data_save = JSON.parse(JSON.stringify(source.data));
        }
        var full_data = window.full_data_save;
        var full_data_length = full_data.x.length;
        var new_data = { x: [], y: [], color: [], title: [], released: [], imdbvotes: [] }
        for (var i = 0; i < full_data_length; ++i) {
            if (full_data.imdbvotes[i] === null || full_data.released[i] === null || full_data.genre[i] === null)
                continue;
            if (
                full_data.imdbvotes[i] > controls.reviews.value &&
                Number(full_data.released[i].slice(-4)) >= controls.min_year.value &&
                Number(full_data.released[i].slice(-4)) <= controls.max_year.value &&
                (controls.genre.value === 'All' ||
                 full_data.genre[i].split(',').some(ele => ele.trim() === controls.genre.value))
            ) {
                Object.keys(new_data).forEach(key => new_data[key].push(full_data[key][i]));
            }
        }

        source.data = new_data;
        source.change.emit();
    """)

    fig = figure(plot_height=600, plot_width=720,
                 tooltips=[('Title', '@title'), ('Released', '@released')])
    fig.circle(x='x', y='y', source=source, size=5, color='color', line_color=None)
    fig.xaxis.axis_label = 'IMDB Rating'
    fig.yaxis.axis_label = 'Rotten Tomatoes Rating'

    curr_movies = selected_movies()

    source.data = dict(
        x=[d['imdbrating'] for d in curr_movies],
        y=[d['numericrating'] for d in curr_movies],
        color=['#FF9900' for d in curr_movies],
        title=[d['title'] for d in curr_movies],
        released=[d['released'] for d in curr_movies],
        imdbvotes=[d['imdbvotes'] for d in curr_movies],
        genre=[d['genre'] for d in curr_movies]
    )

    for single_control in controls_array:
        single_control.js_on_change('value', callback)

    inputs_column = column(*controls_array, width=320, height=1000)

    script, div = components(row([inputs_column, fig]))
    return render_template_string("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    {{ js_resources|indent(4)|safe }}
    {{ css_resources|indent(4)|safe }}
    {{ plot_script|indent(4)|safe }}
</head>
<body>
    <h1 style="text-align: center; margin-bottom: 40px;">Flask + Bokeh + EasyBase.io</h2>
    <div style="display: flex; justify-content: center;">
        {{ plot_div|indent(4)|safe }}
    </div>
</body>
</html>""", plot_script=script, plot_div=div,
                                  js_resources=INLINE.render_js(),
                                  css_resources=INLINE.render_css())


if __name__ == '__main__':
    app.run(debug=True)
