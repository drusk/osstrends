/******************************************************************************
 * Copyright (C) 2013 David Rusk
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 *****************************************************************************/

/**
 * Creates a bar chart for the specified language statistics.
 *
 * @param id The DOM id of the element to draw the chart on.  Should be a
 * canvas element.
 * @param language_stats Object with languages as keys and number of bytes
 * as values.
 */
function createBarChart(id, language_stats) {
    var labels = [];
    var data = [];

    for (var language in language_stats) {
        var count = language_stats[language];
        labels.push(language);
        data.push(count);
    }

    var context = document.getElementById(id).getContext("2d");
    var chart = new Chart(context).Bar(
        {
            labels: labels,
            datasets: [
                {
                    fillColor: "rgba(110,220,110,0.5)",
                    strokeColor: "rgba(110,110,110,1)",
                    data: data
                }
            ]
        }
    )
}
