import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('data/processed/WorkingHours_cleaned.csv')

app = dash.Dash(__name__)


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
        options=[{'label': task_category, 'value': task_category}
                 for task_category in df['Task Category'].unique()],
        value=df['Task Category'].unique(),  # Default to all tasks
        multi=True,
        placeholder="Select Task(s)"
    ),

    # Graph 1: Daily Study Time
    dcc.Graph(id='daily-study-time'),

    # Graph 2: Task Distribution (Stacked Bar Chart)
    dcc.Graph(id='task-distribution-stacked'),

    # Graph 3: Most Time-Consuming Task per Month
    dcc.Graph(id='most-time-task-month'),

    # Graph 4: Task Percentage Time Series
    dcc.Graph(id='task-percentage-time-series'),


])


@app.callback(
    [
        Output('daily-study-time', 'figure'),
        Output('task-distribution-stacked', 'figure'),
        Output('most-time-task-month', 'figure'),
        Output('task-percentage-time-series', 'figure'),
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

    fig1.update_layout(
        plot_bgcolor='white'
    )

    fig1.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig1.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    # Graph 2: Task Distribution (Stacked Bar Chart)
    task_distribution = filtered_df.groupby(
        ['Day', 'Task Category'])['Duration']\
        .sum()\
        .reset_index()

    fig2 = px.bar(
        task_distribution,
        x='Day',
        y='Duration',
        color='Task Category',
        title='Task Category Distribution ',
        color_discrete_sequence=px.colors.qualitative.Antique
    )

    fig2.update_layout(
        plot_bgcolor='white'
    )

    fig2.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig2.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    # Graph 3: Most Time-Consuming Task per Month
    most_time_task_month = filtered_df.groupby(
        ['Month', 'Task Category'])['Duration']\
        .sum()\
        .reset_index()

    most_time_task_month = most_time_task_month.loc[most_time_task_month.groupby('Month')[
        'Duration']
        .idxmax()]

    fig3 = px.bar(
        most_time_task_month,
        x='Month',
        y='Duration',
        color='Task Category',
        title='Most Time-Consuming Task per Month',
        color_discrete_sequence=px.colors.qualitative.Antique
    )

    fig3.update_layout(
        plot_bgcolor='white'
    )

    fig3.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig3.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    # Graph 4
    total_duration_per_day = filtered_df.groupby(
        'Month')['Duration'].sum().reset_index()
    total_duration_per_day = total_duration_per_day.rename(
        columns={'Duration': 'Total_Duration'})

    # Merge total duration with the filtered dataframe
    task_percentage = filtered_df.merge(total_duration_per_day,
                                        on='Month')

    # Calculate percentage of time spent on each task per day
    task_percentage['Percentage'] = (
        task_percentage['Duration'] / task_percentage['Total_Duration']) * 100

    fig4 = px.area(
        task_percentage,
        x='Month',
        y='Percentage',
        color='Task Category',
        title='Percentage of Time Spent on Tasks Over Time',
        labels={'Percentage': 'Percentage of Time (%)'},
        color_discrete_sequence=px.colors.qualitative.Antique,
        groupnorm='percent',
        line_shape='hvh'

    )

    fig4.update_layout(
        plot_bgcolor='white'
    )

    fig4.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig4.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig4.for_each_trace(lambda trace: trace.update(fillcolor=trace.line.color))

    return fig1, fig2, fig3, fig4


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
