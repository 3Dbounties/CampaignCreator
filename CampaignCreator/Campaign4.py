import sys
import json
import webbrowser
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QWidget, QScrollArea, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

# Load question data from JSON files
def load_questions_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# JSON formatted questions
json_files = [
    'CampaignOverview.json', 'CampaignMechanics.json', 'PlotandStory.json', 'Locations.json',
    'PlayerInvolvementandAgency.json', 'FactionsandOrganizations.json', 'NPCs.json',
    'EncountersandChallenges.json', 'SideQuestsandExploration.json', 'MagicandItems.json',
    'CampaignConclusion.json'
]
questions_data = [load_questions_data(file) for file in json_files]

class MultiSelectWidget(QWidget):
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.checkboxes = [QCheckBox(option) for option in options]
        for checkbox in self.checkboxes:
            self.layout.addWidget(checkbox)

        self.custom_option = QLineEdit(self)
        self.custom_option.setPlaceholderText("Enter custom option")
        self.layout.addWidget(self.custom_option)

    def get_selected_options(self):
        selected_options = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        custom_text = self.custom_option.text().strip()
        if (custom_text):
            selected_options.append(custom_text)
        return selected_options

class CampaignConfigurator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("D&D Campaign Configurator")
        self.setGeometry(100, 100, 1200, 800)

        self.setFont(QFont("Garamond", 12))

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#F5F5DC"))
        self.setPalette(palette)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(50, 50, 1100, 700)

        self.selected_options = {}

        tab_names = [
            "Campaign Overview", "Campaign Mechanics", "Plot and Story", "Locations",
            "Player Involvement and Agency", "Factions and Organizations", "NPCs",
            "Encounters and Challenges", "Side Quests and Exploration", "Magic and Items",
            "Campaign Conclusion"
        ]

        for tab_name, question_data in zip(tab_names, questions_data):
            self.add_tab(tab_name, question_data)

        self.add_buttons()

    def add_tab(self, tab_name, questions_data):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll_area = QScrollArea(tab)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)

        container_widget = QWidget()
        scroll_area.setWidget(container_widget)

        container_layout = QVBoxLayout(container_widget)

        for question in questions_data["questions"]:
            question_label = QLabel(question["question"])
            question_label.setStyleSheet("color: #8B4513; font: bold 12px;")
            container_layout.addWidget(question_label)

            multi_select_widget = MultiSelectWidget(question["options"])
            container_layout.addWidget(multi_select_widget)

            self.selected_options[(tab_name, question["question"])] = multi_select_widget

        layout.addWidget(scroll_area)
        self.tab_widget.addTab(tab, tab_name)

    def add_buttons(self):
        button_layout = QHBoxLayout()
        clear_all_button = QPushButton("Clear All Selections", self)
        clear_all_button.clicked.connect(self.clear_all_selections)
        clear_all_button.setStyleSheet("background-color: #8B4513; color: #FFD700; font: bold 14px;")

        clear_current_tab_button = QPushButton("Clear Current Tab Selections", self)
        clear_current_tab_button.clicked.connect(self.clear_current_tab_selections)
        clear_current_tab_button.setStyleSheet("background-color: #8B4513; color: #FFD700; font: bold 14px;")

        submit_button = QPushButton("Submit", self)
        submit_button.clicked.connect(self.submit)
        submit_button.setStyleSheet("background-color: #8B4513; color: #FFD700; font: bold 14px;")

        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(clear_current_tab_button)
        button_layout.addWidget(submit_button)

        button_container = QWidget(self)
        button_container.setLayout(button_layout)
        button_container.setGeometry(50, 760, 1100, 40)

    def submit(self, _):
        selected = {}
        for (tab_name, question), multi_select_widget in self.selected_options.items():
            selected_values = multi_select_widget.get_selected_options()
            if selected_values:
                if tab_name not in selected:
                    selected[tab_name] = {}
                selected[tab_name][question] = selected_values

        self.export_to_browser(selected)
        self.export_to_json(selected)  # New method call

    def export_to_json(self, selected):
        try:
            json_output = json.dumps(selected, indent=4)
            with open('campaign_selections.json', 'w') as json_file:
                json_file.write(json_output)
            print("Selections exported to campaign_selections.json")
        except Exception as e:
            print(f"Failed to export selections to JSON: {e}")

    def export_to_browser(self, selected):
        try:
            tabs = [
                "Campaign Overview", "Campaign Mechanics", "Plot and Story", "Locations",
                "Player Involvement and Agency", "Factions and Organizations", "NPCs",
                "Encounters and Challenges", "Side Quests and Exploration", "Magic and Items",
                "Campaign Conclusion"
            ]

            html_content = '''
            <html>
            <head>
                <style>
                    body { font-family: 'Garamond', serif; background-color: #F5F5DC; color: #8B4513; padding: 20px; }
                    h1, h2 { color: #8B0000; }
                    h3 { color: #DAA520; }
                    ul { list-style-type: square; }
                    li { margin-bottom: 5px; }
                    .tab { overflow: hidden; border: 1px solid #ccc; }
                    .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
                    .tab button:hover { background-color: #ddd; }
                    .tab button.active { background-color: #8B0000; color: #FFD700; }
                    .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
                    .tabcontent h2, .tabcontent p { color: #8B4513; }
                </style>
                <script>
                    function openTab(evt, tabName) {
                        var i, tabcontent, tablinks;
                        tabcontent = document.getElementsByClassName("tabcontent");
                        for (i = 0; i < tabcontent.length; i++) {
                            tabcontent[i].style.display = "none";
                        }
                        tablinks = document.getElementsByClassName("tablinks");
                        for (i = 0; i < tablinks.length; i++) {
                            tablinks[i].className = tablinks[i].className.replace(" active", "");
                        }
                        document.getElementById(tabName).style.display = "block";
                        evt.currentTarget.className += " active";
                    }
                </script>
            </head>
            <body>
                <h1>Campaign Selections</h1>
                <div class="tab">
            '''

            html_content += ''.join(f'<button class="tablinks" onclick="openTab(event, \'{tab.replace(" ", "_")}\')">{tab}</button>' for tab in tabs)
            html_content += '</div>'

            for tab in tabs:
                html_content += f'<div id="{tab.replace(" ", "_")}" class="tabcontent">'
                html_content += f'<h2>{tab}</h2>'
                if tab in selected:
                    for question, answers in selected[tab].items():
                        html_content += f'<p>{question}</p><ul>'
                        html_content += ''.join(f'<li>{answer}</li>' for answer in answers)
                        html_content += '</ul>'
                else:
                    html_content += '<p>No selections made.</p>'
                html_content += '</div>'

            html_content += '''
                <script>
                    document.getElementsByClassName("tablinks")[0].click();
                </script>
            </body>
            </html>
            '''

            # Use a temporary file to open the HTML content in the default browser
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as temp_file:
                temp_file.write(html_content)
                temp_file.flush()
                webbrowser.open(f'file://{temp_file.name}')
                
        except Exception as e:
            print(f"Failed to open selections in browser: {e}")

    def clear_all_selections(self):
        for multi_select_widget in self.selected_options.values():
            for checkbox in multi_select_widget.checkboxes:
                checkbox.setChecked(False)
            multi_select_widget.custom_option.clear()
        print("All selections have been cleared.")

    def clear_current_tab_selections(self):
        current_tab_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        for (tab_name, question), multi_select_widget in self.selected_options.items():
            if tab_name == current_tab_name:
                for checkbox in multi_select_widget.checkboxes:
                    checkbox.setChecked(False)
                multi_select_widget.custom_option.clear()
        print(f"Selections for the tab '{current_tab_name}' have been cleared.")

def main():
    app = QApplication(sys.argv)
    window = CampaignConfigurator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
