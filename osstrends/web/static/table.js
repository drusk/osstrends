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
 * Creates a DataTable out of the specified table.
 *
 * @param elementId String containing the id of the table holding the data.
 *        Example: "#user_table".
 * @param sortColumn Integer indicating the 0-based index of the column to
 *        sort on by default (descending).
 * @param direction String indicating sort direction.  "asc" for ascending
 *        or "desc" for descending.
 */
function createDataTable(elementId, sortColumn, direction) {
    if (elementId[0] != "#") {
        elementId = "#" + elementId;
    }

    var dataTable = $(elementId).dataTable({
        "sPaginationType": "bs_full",
        "oLanguage": {
            "sSearch": "Search Fields:"
        }
    });

    dataTable.fnSort([[sortColumn, direction]]);
}