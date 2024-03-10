import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Создание данных для графика
x_data = [1, 2, 3, 4, 5]
y_data = [1, 3, 2, 4, 3]
data2 = [2, 4, 1, 3, 2, 4]

# Создание экземпляра приложения Dash
app = dash.Dash(__name__)

# Определение макета веб-приложения
app.layout = html.Div(children=[
    html.H1(children='График с действием при нажатии на точку'),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': x_data, 'y': y_data, 'type': 'scatter', 'mode': 'markers+lines'},
                {'x': x_data, 'y': y_data, 'type': 'scatter', 'mode': 'markers+lines'},
            ],
            'layout': {
                'title': 'Пример графика',
                'clickmode': 'event+select',
                'width': '1000px',
            }
        }
    ),
    dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': x_data, 'y': y_data, 'type': 'scatter', 'mode': 'markers+lines'},
                    {'x': x_data, 'y': y_data, 'type': 'scatter', 'mode': 'markers+lines'},
                ],
                'layout': {
                    'title': 'Пример графика',
                    'clickmode': 'event+select',
                    'width': '200px',
                }
            }
        ),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': x_data, 'y': y_data, 'type': 'scatter', 'mode': 'markers+lines'},
                {'x': x_data, 'y': y_data, 'type': 'scatter', 'mode': 'markers+lines'},
            ],
            'layout': {
                'title': 'Пример графика',
                'clickmode': 'event+select',
                'width': '400px',
                'height': '400px'
            }
        }
    ),
    html.Div(id='output')
])

# Функция обратного вызова для отображения информации о нажатой точке
@app.callback(
    Output('output', 'children'),
    [Input('example-graph', 'clickData')])
def display_click_data(clickData):
    if clickData is not None:
        point = clickData['points'][0]
        x_value = point['x']
        y_value = point['y']
        return f'Нажатая точка: x={x_value}, y={y_value}'
    else:
        return ''

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
