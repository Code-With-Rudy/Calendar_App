import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QHBoxLayout, QWidget,
    QCalendarWidget, QListWidget,
    QPushButton, QLineEdit, QDialog,
    QLabel, QMessageBox, QDateTimeEdit
)
from PyQt5.QtCore import QDate, QDateTime, Qt, QTime
from PyQt5.QtGui import QIcon

class CalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar & Reminder App")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('F:/WEB Development/pinacle_labs_Projects/calendar.png'))
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        calendar_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked[QDate].connect(self.show_reminders_for_date)
        calendar_layout.addWidget(self.calendar)
        main_layout.addLayout(calendar_layout)
        reminders_layout = QVBoxLayout()
        self.reminders_label = QLabel("Reminders for Selected Date:")
        reminders_layout.addWidget(self.reminders_label)
        self.reminders_list = QListWidget()
        reminders_layout.addWidget(self.reminders_list)
        button_layout = QHBoxLayout()
        self.add_reminder_button = QPushButton("Add Reminder")
        self.add_reminder_button.clicked.connect(self.add_reminder)
        button_layout.addWidget(self.add_reminder_button)
        self.edit_reminder_button = QPushButton("Edit Reminder")
        self.edit_reminder_button.clicked.connect(self.edit_reminder)
        button_layout.addWidget(self.edit_reminder_button)
        self.delete_reminder_button = QPushButton("Delete Reminder")
        self.delete_reminder_button.clicked.connect(self.delete_reminder)
        button_layout.addWidget(self.delete_reminder_button)
        reminders_layout.addLayout(button_layout)
        main_layout.addLayout(reminders_layout)
        self.reminders = {}
        self.show_reminders_for_date(QDate.currentDate())

    def show_reminders_for_date(self, date):
        self.reminders_list.clear()
        self.reminders_label.setText(f"Reminders for {date.toString(Qt.ISODate)}:")
        if date in self.reminders:
            for reminder_text in self.reminders[date]:
                self.reminders_list.addItem(reminder_text)

    def add_reminder(self):
        selected_date = self.calendar.selectedDate()
        dialog = AddReminderDialog(selected_date, self)
        if dialog.exec_() == QDialog.Accepted:
            reminder_text = dialog.get_reminder_text()
            reminder_datetime = dialog.get_reminder_datetime()
            formatted_reminder = f"{reminder_datetime.toString('hh:mm')} - {reminder_text}" if reminder_datetime else reminder_text
            self.reminders.setdefault(selected_date, []).append(formatted_reminder)
            self.show_reminders_for_date(selected_date)
            QMessageBox.information(self, "Reminder Added", "Reminder has been successfully added.")

    def edit_reminder(self):
        selected_date = self.calendar.selectedDate()
        selected_items = self.reminders_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Reminder Selected", "Please select a reminder to edit.")
            return
        current_reminder_text = selected_items[0].text()   
        original_time_str = None
        original_text_only = current_reminder_text
        if " - " in current_reminder_text:
            parts = current_reminder_text.split(" - ", 1)
            try:
                QTime.fromString(parts[0], 'hh:mm')
                original_time_str = parts[0]
                original_text_only = parts[1]
            except Exception:
                pass

        dialog = AddReminderDialog(selected_date, self, current_reminder_text=original_text_only, current_time_str=original_time_str)
        if dialog.exec_() == QDialog.Accepted:
            new_reminder_text = dialog.get_reminder_text()
            new_reminder_datetime = dialog.get_reminder_datetime()
            formatted_new_reminder = f"{new_reminder_datetime.toString('hh:mm')} - {new_reminder_text}" if new_reminder_datetime else new_reminder_text
            if selected_date in self.reminders:
                try:
                    index = self.reminders[selected_date].index(current_reminder_text)
                    self.reminders[selected_date][index] = formatted_new_reminder
                    self.show_reminders_for_date(selected_date)
                    QMessageBox.information(self, "Reminder Edited", "Reminder has been successfully edited.")
                except ValueError:
                    QMessageBox.critical(self, "Error", "Selected reminder not found in list.")
            else:
                QMessageBox.critical(self, "Error", "No reminders found for this date.")

    def delete_reminder(self):
        selected_date = self.calendar.selectedDate()
        selected_items = self.reminders_list.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "No Reminder Selected", "Please select a reminder to delete.")
            return

        reply = QMessageBox.question(self, "Delete Reminder","Are you sure you want to delete this reminder?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            reminder_to_delete = selected_items[0].text()
            if selected_date in self.reminders:
                self.reminders[selected_date].remove(reminder_to_delete)
                if not self.reminders[selected_date]:
                    del self.reminders[selected_date]
                self.show_reminders_for_date(selected_date)
                QMessageBox.information(self, "Reminder Deleted", "Reminder has been successfully deleted.")
            else:
                QMessageBox.critical(self, "Error", "No reminders found for this date.")

class AddReminderDialog(QDialog):
    def __init__(self, date, parent=None, current_reminder_text="", current_time_str=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add/Edit Reminder for {date.toString(Qt.ISODate)}")
        self.setFixedSize(400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.text_label = QLabel("Reminder Text:")
        self.layout.addWidget(self.text_label)
        self.reminder_text_input = QLineEdit()
        self.reminder_text_input.setText(current_reminder_text)
        self.layout.addWidget(self.reminder_text_input)
        self.time_label = QLabel("Set Time (Optional):")
        self.layout.addWidget(self.time_label)
        self.reminder_time_input = QDateTimeEdit(self)
        self.reminder_time_input.setCalendarPopup(True)
        self.reminder_time_input.setDisplayFormat("hh:mm")
        self.reminder_time_input.setDateTime(QDateTime.currentDateTime())
        self.reminder_time_input.setMinimumDateTime(QDateTime(date, QTime(0, 0)))
        self.reminder_time_input.setMaximumDateTime(QDateTime(date, QTime(23, 59, 59)))
        
        if current_time_str:
            time_obj = QTime.fromString(current_time_str, 'hh:mm')
            if time_obj.isValid():
                self.reminder_time_input.setDateTime(QDateTime(date, time_obj))
            else:
                self.reminder_time_input.setDateTime(QDateTime.currentDateTime())
        else:
            self.reminder_time_input.setDateTime(QDateTime.currentDateTime())

        self.layout.addWidget(self.reminder_time_input)
        self.button_box = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.button_box.addWidget(self.save_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_box)

    def get_reminder_text(self):
        return self.reminder_text_input.text()

    def get_reminder_datetime(self):
        return self.reminder_time_input.dateTime()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())
