import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('data/processed/WorkingHours_cleaned.csv')
df['Day'] = pd.to_datetime(df['Day'])
df['Month'] = df['Day'].dt.to_period('M').astype(str)
df['Duration'] = df['Duration'].str.replace(' min', '').astype(int)
df['Task'] = df['Task'].fillna('Other')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Study Time Dashboard"),

    # Date Range Picker
    dcc.DatePickerRange(
        id='date-range',
        start_date=df['Day'].min(),
        end_date=df['Day'].max(),
        display_format='YYYY/MM/DD'
    ),

    # Task Filter
    dcc.Dropdown(
        id='task-filter',
        options=[{'label': task, 'value': task}
                 for task in df['Task'].unique()],
        value=df['Task'].unique(),  # Default to all tasks
        multi=True,
        placeholder="Select Task(s)"
    ),

    # Graph 1: Daily Study Time
    dcc.Graph(id='daily-study-time'),

    # Graph 2: Task Distribution (Stacked Bar Chart)
    dcc.Graph(id='task-distribution-stacked'),

    # Graph 3: Most Time-Consuming Task per Month
    dcc.Graph(id='most-time-task-month'),

])

# Callback to update graphs based on filters


@app.callback(
    [
        Output('daily-study-time', 'figure'),
        Output('task-distribution-stacked', 'figure'),
        Output('most-time-task-month', 'figure'),
    ],

    [
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('task-filter', 'value')
    ]
)
def update_graphs(start_date, end_date, selected_tasks):

    filtered_df = df[(df['Day'] >= start_date) & (df['Day'] <= end_date)]
    if selected_tasks:
        filtered_df = filtered_df[filtered_df['Task'].isin(selected_tasks)]

    # Graph 1: Daily Study Time
    daily_study_time = filtered_df.groupby(
        'Day')['Duration'] \
        .sum() \
        .reset_index()

    fig1 = px.bar(
        daily_study_time,
        x='Day',
        y='Duration',
        title='Daily Study Time',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # Graph 2: Task Distribution (Stacked Bar Chart)
    task_distribution = filtered_df.groupby(
        ['Day', 'Task'])['Duration']\
        .sum()\
        .reset_index()

    fig2 = px.bar(
        task_distribution,
        x='Day',
        y='Duration',
        color='Task',
        title='Task Distribution ',
        barmode='stack')

    # Graph 3: Most Time-Consuming Task per Month
    most_time_task_month = filtered_df.groupby(
        ['Month', 'Task'])['Duration']\
        .sum()\
        .reset_index()

    most_time_task_month = most_time_task_month.loc[most_time_task_month.groupby('Month')[
        'Duration']
        .idxmax()]

    fig3 = px.bar(
        most_time_task_month,
        x='Month',
        y='Duration',
        color='Task',
        title='Most Time-Consuming Task per Month',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    return fig1, fig2, fig3


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
