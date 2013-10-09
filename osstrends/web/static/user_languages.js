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
 * @param language_stats an array of languages, where each language is an
 * array of size two with the first element being the language name and
 * the second value being the number of bytes.
 * Ex: [["JavaScript", 1667724], ["Python", 1808338]]
 */
function createBarChart(id, language_stats) {
    var labels = [];
    var data = [];

    for (var i = 0; i < language_stats.length; i++) {
        var language_count = language_stats[i];
        labels.push(language_count[0]);
        data.push(language_count[1]);
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
