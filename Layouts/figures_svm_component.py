import colorlover as cl
import plotly.graph_objs as go
import numpy as np
from collections import OrderedDict
from sklearn import metrics

from Controllers.statistics_controller import DataService, initialization




def serve_prediction_plot(model,
                          X_train,
                          X_test,
                          y_train,
                             y_test,
                          Z,
                          xx,
                          yy,
                          mesh_step,
                          threshold):
    # Get train and test score from model
    y_pred_train = (model.decision_function(X_train) > threshold).astype(int)
    y_pred_test = (model.decision_function(X_test) > threshold).astype(int)
    train_score = metrics.accuracy_score(y_true=y_train, y_pred=y_pred_train)
    test_score = metrics.accuracy_score(y_true=y_test, y_pred=y_pred_test)

    # Compute threshold
    scaled_threshold = threshold * (Z.max() - Z.min()) + Z.min()
    range = max(abs(scaled_threshold - Z.min()),
                abs(scaled_threshold - Z.max()))

    # Colorscale
    bright_cscale = [[0, '#FF0000'], [1, '#0000FF']]

    colorscale_zip = zip(np.arange(0, 1.01, 1 / 8),
                         cl.scales['9']['div']['RdBu'])
    cscale = list(map(list, colorscale_zip))

    # Create the plot
    # Plot the prediction contour of the SVM
    trace0 = go.Contour(
        x=np.arange(xx.min(), xx.max(), mesh_step),
        y=np.arange(yy.min(), yy.max(), mesh_step),
        z=Z.reshape(xx.shape),
        zmin=scaled_threshold - range,
        zmax=scaled_threshold + range,
        hoverinfo='none',
        showscale=False,
        contours=dict(
            showlines=False
        ),
        colorscale=cscale,
        opacity=0.9
    )

    # Plot the threshold
    trace1 = go.Contour(
        x=np.arange(xx.min(), xx.max(), mesh_step),
        y=np.arange(yy.min(), yy.max(), mesh_step),
        z=Z.reshape(xx.shape),
        showscale=False,
        hoverinfo='none',
        contours=dict(
            showlines=False,
            type='constraint',
            operation='=',
            value=scaled_threshold,
        ),
        name=f'Umbral-Threshold ({scaled_threshold:.3f})',
        line=dict(
            color='#222222'
        )
    )

    # Plot Training Data
    trace2 = go.Scatter(
        x=X_train[:, 0],
        y=X_train[:, 1],
        mode='markers',
        name=f'Training Data (Presición- accuracy={train_score:.3f})',
        marker=dict(
            size=10,
            color=y_train,
            colorscale=bright_cscale,
            line=dict(
                width=1
            )
        )
    )

    # Plot Test Data
    trace3 = go.Scatter(
        x=X_test[:, 0],
        y=X_test[:, 1],
        mode='markers',
        name=f'Test Data (Presición- accuracy={test_score:.3f})',
        marker=dict(
            size=10,
            symbol='triangle-up',
            color=y_test,
            colorscale=bright_cscale,
            line=dict(
                width=1
            ),
        )
    )

    layout = go.Layout(
        xaxis=dict(
            # scaleanchor="y",
            # scaleratio=1,
            ticks='',
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            ticks='',
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        hovermode='closest',
        legend=dict(x=0, y=-0.01, orientation="h"),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    data = [trace0, trace1, trace2, trace3]
    figure = go.Figure(data=data, layout=layout)

    return figure


def serve_roc_curve(model,
                    X_test,
                    y_test):
    decision_test = model.decision_function(X_test)
    fpr, tpr, threshold = metrics.roc_curve(y_test, decision_test)

    # AUC Score
    auc_score = metrics.roc_auc_score(y_true=y_test, y_score=decision_test)

    trace0 = go.Scatter(
        x=fpr,
        y=tpr,
        mode='lines',
        name='Test Data',
    )

    layout = go.Layout(
        title=f'ROC Curve (AUC = {auc_score:.3f})',
        xaxis=dict(
            title='False Positive Rate'
        ),
        yaxis=dict(
            title='True Positive Rate'
        ),
        legend=dict(x=0, y=1.05, orientation="h"),
        margin=dict(l=50, r=10, t=55, b=40),
    )

    data = [trace0]
    figure = go.Figure(data=data, layout=layout)

    return figure


def serve_pie_confusion_matrix(model,
                               X_test,
                               y_test,
                               Z,
                               threshold):
    # Compute threshold
    scaled_threshold = threshold * (Z.max() - Z.min()) + Z.min()
    y_pred_test = (model.decision_function(X_test) > scaled_threshold).astype(int)

    matrix = metrics.confusion_matrix(y_true=y_test, y_pred=y_pred_test)
    tn, fp, fn, tp = matrix.ravel()

    values = [tp, fn, fp, tn]
    label_text = ["Verdadero Positivo",
                  "Falso Negativo",
                  "Falso Positivo",
                  "Verdadero Negativo"]
    labels = ["VP", "FN", "FP", "VN"]
    blue = cl.flipper()['seq']['9']['Blues']
    red = cl.flipper()['seq']['9']['Reds']
    colors = [blue[4], blue[1], red[1], red[4]]

    trace0 = go.Pie(
        labels=label_text,
        values=values,
        hoverinfo='label+value+percent',
        textinfo='text+value',
        text=labels,
        sort=False,
        marker=dict(
            colors=colors
        )
    )

    layout = go.Layout(
        title=f'Matriz de Confusión',
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(
            bgcolor='rgba(255,255,255,0)',
            orientation='h'
        )
    )

    data = [trace0]
    figure = go.Figure(data=data, layout=layout)

    return figure

def frecuency_table():
    figure = go.Figure(
        data=initialization.df_data,
        layout=go.Layout(
            xaxis=dict(zeroline=False),
            yaxis=dict(
                title=dict(
                    text="Conc (uM)",
                    font=dict(
                        family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                        " Helvetica, Arial, sans-serif",
                        size=12,
                    ),
                ),
                type="log",
                rangemode="tozero",
                zeroline=False,
                showticklabels=False,
            ),
            margin=dict(l=40, r=30, b=50, t=50),
            showlegend=False,
            height=294,
            paper_bgcolor="rgb(245, 247, 249)",
            plot_bgcolor="rgb(245, 247, 249)",
        ),
    )
    list_frec = list(initialization.df_frecuency)
    columns = (
        [{"name": "Parameter", "id": "param"}]
        + {"name": "-", "id": "-"}+[
            {
                "name": subject,
                "id": str(subject),
                "type": "str",
            }
            for subject in list_frec
        ]

    )
    result_names = OrderedDict(
        count= 'count',
        mean= 'mean',
        std= 'std',
        min= 'min',
        _25= '25%',
        _50= '50%',
        _75= '75%',
        max= 'max'
    )

    data = []
    for key, name in result_names.items():
        d = dict(param=name)
        for subject in list_frec:
            d[int(subject)] = getattr(initialization.df_data[subject], key)

        data.append(d)

    return figure, columns, data
