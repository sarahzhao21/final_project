from flask import Flask, render_template, request
import sqlite3
import plotly.graph_objects as go

app = Flask(__name__)

def get_results(category, sort_by, sort_order):
    conn = sqlite3.connect('best_seller_books.sqlite')
    cur = conn.cursor()
    
    if sort_by == 'Rank':
        sort_column = 'Rank'
    elif sort_by == 'Rating':
        sort_column = 'Rating'
    elif sort_by == 'Price':
        sort_column = 'Price'
    else:
        sort_column = 'Length'

    where_clause = ''
    if (category != 'All'):
        where_clause = f'WHERE Category = "{category}"'

    q = f'''
        SELECT A.Title, A.Genre, B.Author, {sort_column}, Seller  
        FROM Best_seller AS B
        JOIN Apple_book AS A
            ON B.Id=A.Id
        {where_clause}
        ORDER BY {sort_column} {sort_order}
        LIMIT 10
    '''
    print(q)
    results = cur.execute(q).fetchall()
    conn.close()
    print(results)
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def books():
    category = request.form['category']
    sort_by = request.form['sort']
    sort_order = request.form['dir']
    
    results = get_results(category, sort_by, sort_order)
    
    plot_results = request.form.get('plot', False)
    if (plot_results):
        x_vals = [r[0] for r in results]
        y_vals = [r[3] for r in results]
        books_data = go.Bar(
            x=x_vals,
            y=y_vals
        )
        fig = go.Figure(data=books_data)
        div = fig.to_html(full_html=False)
        return render_template("plot.html", plot_div=div)
    else:
        return render_template('results.html', 
            sort=sort_by, results=results)


if __name__ == '__main__':
    app.run(debug=True)