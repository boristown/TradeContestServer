global user_token
self.main_window = toga.MainWindow(title=self.formal_name)
self.tabledata = defaultdict(list)
self.realtabledata = defaultdict(list)
content = self.market_page()
self.main_window.content = content
self.main_window.show()