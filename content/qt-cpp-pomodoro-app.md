Title: Learning Qt and C++ by making a Pomodoro timer
Summary: A C++ dummy learns the language and Qt
Authour: Oscar Peace
Tags: C++
      Qt
      Projects
Published: 6/8/2026

For a while now I've wanted to expand my language repertoire. One of the languages that has always looked appealing to me has been C++, but despite my interest in low-level programming - [goputer](https://goputer.oscarcp.net/) being a primary example this. However, up until now I've always passed up any project which might be an opportunity for learning the language.

Recently though, I made the move from Windows to Linux (specifically Fedora), as using Windows was getting to me. That's a secondary reason for this project though. More importantly, I didn't like using a website for a pomodoro timer and applications for the KDE desktop environment are predominantly written in C++. So finally a valid excuse to learn this language that *shouldn't* require too much thought and work.

**Note:** Don't take the examples in this article as gospel. In fact, there are many things in them which are bad practice, take them more as a vague idea of C++ and Qt.

# Setting up Qt

Before using C++, I had predominantly used languages with built-in default package managers. C++ does not have this kind of thing. However, there are "community" built package managers, namely [conan](https://conan.io/) and [vcpkg](https://vcpkg.io/en/) (Microsoft). Qt is available through both of these package managers, but as I found out, it is harder to set up using a package manager than just installing it through the conventional system package manager instead. When I tried to use vcpkg/conan to set it up it wouldn't build, I had to build Qt from scratch, no window would show up, it would crash immediately, and the list goes on. Because troubleshooting this *really* wasn't worth my time, I decided to stick to using the system packages instead.

# Baby's first window

After getting Qt set up, the next thing to do was to draw a window to the screen - I had done this already, albeit non-functional. I used QtDesigner for the UI, because while QML looked nice, I wanted something where I had to write fewer lines of code for the UI. I'm aware Designer just generates header files for you, but these generated headers seemed easier to integrate with C++. I might use QML for a future project though, as the handling of slots, signals, and updating state seems easier. Anyway, that's for another time, here's the main window initialisation:

```cpp

...

QT_BEGIN_NAMESPACE
namespace Ui {class MainAppWindow;}
QT_END_NAMESPACE

const auto TIMER_START = "Start";
const auto TIMER_PAUSE = "Pause";
const auto TIMER_SKIP = "Skip";

class MainAppWindow : public QMainWindow {
    Q_OBJECT

    public:
        explicit MainAppWindow(QWidget *parent = nullptr);
        ~MainAppWindow();

    private slots:
        void openSettingsDialog();
        void openStatsDialog();

    private:
        Ui::MainAppWindow *m_ui;
        TimerModel *m_timer_model;
        void setStatsText(TimerStats timer_stats);
        QSystemTrayIcon *m_sys_tray;
        void closeEvent(QCloseEvent *event) override;
};
```

You'll see at the top the `QT_BEGIN_NAMESPACE` and `QT_END_NAMESPACE`, this allows us to include the generated main window class. Next are some constant strings, but these should be Qt's translatable strings. After that `Q_OBJECT` annotates the class to work properly with Qt. 

You'll see the `private slots` section here as well, **slots** in Qt are special methods which you can connect with **signals**. For example, button would emit a signal when pressed, which can then be connected to a `whenButtonClicked` slot. Of course there are other signals as well, see the list of signals for the base `QAbstractButton` class in the [Qt documentation](https://doc.qt.io/qt-6/qabstractbutton.html#signals) for more examples. It is important to note that slots and signals are just regular C++ methods and can still be used as such.

Finally the `closeEvent` method is overridden so we can minimise to the system tray instead of immediately exiting the application.

# The timer model

The state of the application is controlled with a `TimerModel`, roughly following a [MVC pattern](https://doc.qt.io/qt-6/model-view-programming.html). The header for the model is much larger than the main page listed above.

```cpp
...

class TimerModel : public QObject {
    Q_OBJECT

public:
    explicit TimerModel(QObject *parent = nullptr);

    ...

    std::vector<std::array<int64_t, 2>> getData(ColumnType column, std::chrono::seconds start, std::chrono::seconds end) const;

public slots:
    void startPauseTimer();
    void stopTimer();

signals:
    void timerChanged(int newTime);
    void timerStateChanged(TimerState state);
    void statsChanged(TimerStats newStats);

private:
    
    ...

    /// @brief QTimer object used for intervals
    QTimer *m_timer;
    Database *m_db;

    ...
};
```

Firstly, the `getData` method is a wrapper around the databases own method for retrieving data, so we don't expose the database object to other classes. The slots are connected to buttons in the UI, and the signals are used to update the text in the UI; they are also used to write new information to the database and config file.

The [`QTimer`](https://doc.qt.io/qt-6/qtimer.html) (`*m_timer`) is essentially what it says. If you've used JavaScript before you can think of it as calling [`window.setInterval`](https://developer.mozilla.org/en-US/docs/Web/API/Window/setInterval).  

```cpp
m_timer = new QTimer(this);
m_timer->callOnTimeout([this]()
                        {
    if (m_in_work_session)
    {
        m_timer_stats.ms_worked += 1000;
        m_config.total_time_elapsed += 1000;
        m_db->updateEntry(ColumnType::time_worked, 1000);
        emit statsChanged(m_timer_stats);
    }
    this->modifyTime(-1000);
    emit this->timerChanged(m_time); });
```

Alternatively you can connect a slot to the timer's `timeout()` signal.

# Database integration

I had three possible approaches for database integration.

1. Use a object relational mapper (ORM).
2. Use the sqlite3 library directly.
3. Use Qt's SQL library.

While Qt's SQL library or an ORM seemed much cleaner to use than using the sqlite3 library directly, I wanted experience integrating a C library into my C++, so I went with sqlite3. You can see an example of one of the queries below:

```cpp
void Database::updateEntry(ColumnType column, int delta) const
{
    if (db == nullptr)
        throw std::runtime_error("Database not initialised!");

    // Get the last row in the table
    sqlite3_stmt *raw_last_row_stmt;
    if (sqlite3_prepare_v2(db, "SELECT id FROM sessions ORDER BY id DESC LIMIT 1;", -1, &raw_last_row_stmt, nullptr) != SQLITE_OK)
        throw std::runtime_error(sqlite3_errmsg(db));

    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> last_row_stmt(raw_last_row_stmt, &sqlite3_finalize);

    ...

    int64_t row_id = sqlite3_column_int64(last_row_stmt.get(), 0);

    // Update values in last row
    sqlite3_stmt *raw_update_stmt;
    if (sqlite3_prepare_v2(db, std::format("UPDATE {} SET {} = {} + ? WHERE id = ?", TABLE_NAME, columnName(column), columnName(column)).c_str(), -1, &raw_update_stmt, nullptr) != SQLITE_OK)
        throw std::runtime_error(sqlite3_errmsg(db));

    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> update_stmt(raw_update_stmt, &sqlite3_finalize);

    if (sqlite3_bind_int(update_stmt.get(), 1, delta) != SQLITE_OK || sqlite3_bind_int64(update_stmt.get(), 2, row_id) != SQLITE_OK)
        throw std::runtime_error(sqlite3_errmsg(db));

    if (sqlite3_step(update_stmt.get()) != SQLITE_DONE)
        throw std::runtime_error(sqlite3_errmsg(db));
}
```

Firstly there's a check to see if the database has been initialised. Then we prepare a statement to retrieve the last row of the table. This then gets wrapped in a special smart pointer, in this case a `unique_ptr`. A smart pointer in C++ automatically disposes of the object it points to when the pointer goes out of scope. In this case because the sqlite3 library requires a call to `sqlite3_finalize` to dispose of a statement correctly, we are passing that method to the unique pointer so it knows to call it when the statement is disposed of. This also requires using the `.get()` method on the pointer so we can get the raw pointer wrapped by the smart pointer in order to pass it to C.

The last statement is prepared in the same way, but this time passing the name of the column we would like to update. This formatting approach should never be taken for user submitted data, but in this case it is being taken from an enum (`columnName()`), so it is fine. Additionally, integer values are "bound" to the statement, which is to say the question marks in the statement are replaced with them in a **safe** way, i.e. they won't be interpreted as raw SQL code. The last call to `sqlite3_step` finally executes the statement that was prepared earlier. While it was certainly more verbose than using a standard ORM or Qt's SQL API, I think learnt more than I would've done otherwise.

# Graphs

The final thing I wanted to add now I had a database was a graph displaying the previous weeks statistics[^statsnote]. I used the [QtCharts API](https://doc.qt.io/qt-6/qtcharts-index.html), as the newer QtGraphs API seems to be targeted more at QML rather than the Widgets/Designer API I had been using hitherto. Because the charts API is now officially deprecated, don't take the code below as good practice.

Setting up the basic chart is as follows, and just involves some very basic boilerplate code:

```cpp
m_chart->setTitle("Time Worked");
m_axis_x = new QBarCategoryAxis();
m_axis_y = new QValueAxis();
m_chart->addAxis(m_axis_x, Qt::AlignBottom);
m_chart->addAxis(m_axis_y, Qt::AlignLeft);
m_chart->legend()->setVisible(true);
m_chart->legend()->setAlignment(Qt::AlignBottom);

m_ui->chart->setChart(m_chart);
m_ui->chart->setRenderHint(QPainter::Antialiasing);
```

# Addendum on other UI libraries

I did consider using other UI frameworks/libraries namely [imgui](https://github.com/ocornut/imgui) and [wxWidgets](https://wxwidgets.org/). imgui was a straight rejection, not because of the style of the library, or the process of programming in it, but because of a lack of built-in support for screen readers - the primary reason I am learning C++ is for my final year project, which is going to be educational software. I didn't choose wxWidgets because it's API didn't seem as intuitive as Qt's. 

# Conclusion

This project went better than I thought, at least the code I was writing at the end was much better than the code at the start anyway, which is a hallmark of any good project. As for my opinions on C++, I like it so far, there are some things about it I find quite strange (having moved from being predominantly Go/Python focused), but maybe it'll be here to stay. I think I'll have to do a larger project less focused on UI code to know for sure though.

You can view the source for the project on my GitHub [here](https://github.com/sccreeper/pomodoro/blob/main/src/ui/statsdialog.cpp).

[^statsnote]: I can always change this to add changing the week etc.