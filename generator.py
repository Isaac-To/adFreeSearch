from flask import render_template

async def generateWidgetBar(widgetTasks):
    widgets = '<div class="widgetContainer">'
    for widget in widgetTasks:
        widgets += widget
    widgets += '</div>'
    return widgets

async def generateFooter(start):
    pgButtons = '<div class="footer">'
    if start >= 10:
        pgButtons += render_template('pageChangeButtons.html',
                                    title='Previous Page', startResult=start - 10)
        pgButtons += f'Page {int(start / 10) + 1}'
    pgButtons += render_template('pageChangeButtons.html',
                                title='Next Page', startResult=start + 10)
    pgButtons += '</div>'
    return pgButtons