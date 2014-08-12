#include <QApplication>
#include <QWidget>

// You must manually update the .pro file to include the line
//		QT += webkit 
// in order for this to build with the QWebView widget 
#include <QtWebKit>

#include "ui_pcbmill.h"

int main (int argc, char *argv[])
{
	QApplication app(argc, argv);
		
	Ui::PcbMill ui;
	QWidget* widget = new QWidget;
	ui.setupUi(widget);
	widget->show();
	
	return app.exec();
}