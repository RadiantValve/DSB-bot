import json

class usr_data:

    def __init__(self):
        with open('data.json', 'r') as file:
            self.data = json.load(file)

    def get_users(self):
        usernames = []
        for u in self.data['users']:
            usernames.append(u['name'])
        return usernames
    
    def get_users_sendinfo(self):
        users_return = []
        for i in self.data['users']:
            if i['send-info'] == True:
                users_return.append(i['name'])
        return users_return
    
    def get_user_info(self, username):
        for i in self.data['users']:
            if i['name'] == username:
                return i
    
    def get_user_id(self, username):
        for i in self.data['users']:
            if i['name'] == username:
                return i['id']
        return None
    
    def get_user_data(self, username):
        for i in self.data['users']:
            if i['name'] == username:
                return i['send-data']
        return None
    
    def get_user_time(self, username):
        for i in self.data['users']:
            if i['name'] == username:
                return i['send-time-h'], i['send-time-m']
    
    def add_user(self, name, send_info, send_data, send_h, send_m):
        for u in self.data['users']:
            if name == u['name']:
                print("Error: username already in list!")
                return
            id = u['id'] + 1
        new_user_entry = {
            "id": id,
            "name": name,
            "send-info": send_info,
            "send-data": send_data,
            "send-time-h": send_h,
            "send_time-m": send_m
        }
        self.data['users'].append(new_user_entry)
        with open('data.json', 'w') as usr_lst:
            json.dump(self.data, usr_lst, indent=4)
    
    def del_user(self, username):
        id = self.get_user_id(username)
        with open('data.json', 'r+') as json_file:
            del self.data['users'][id]
            json.dump(self.data, json_file, indent=4)
      
    def user_known(self, username):
        for usr in self.data['users']:
            if usr['name'] == username:
                return True
        return False
    
    def change(self): #used for testin, not relevant
        with open('data.json', 'r+') as json_file:
            self.data['users'][2]['name'] = 'HEHEHEHAW'
            json.dump(self.data, json_file, indent=4)
    
    def change_info(self, username, send_info):
        user_info = self.get_user_info(username)
        if send_info != user_info[2]:
            with open('data.json', 'r+') as json_file:
                self.data['users'][user_info[0]]['send-info'] = send_info
                json.dump(self.data, json_file, indent=4)
        else:
            return '\nno data changed\n'
    
    def change_data(self, username, send_data):
        user_info = self.get_user_info(username)
        if send_data != user_info[3]:
            with open('data.json', 'r+') as json_file:
                self.data['users'][user_info[0]]['send-data'] = send_data
                json.dump(self.data, json_file, indent=4)
        else:
            return '\nno data changed\n'
    
    def change_time(self, username, send_time_h, send_time_m):
        user_info = self.get_user_info(username)
        if (send_time_h != user_info[4]) or (send_time_m != user_info[5]):
            with open('data.json', 'r+') as json_file:
                self.data['users'][user_info[0]]['send-time-h'] = send_time_h
                self.data['users'][user_info[0]]['send-time-m'] = send_time_m
                json.dump(self.data, json_file, indent=4)
        else:
            return '\nno data changed\n'

        


users = usr_data()
#print(users.get_users_sendinfo())
#users.add_user("me", False, None, None, None)
#print("\n\n\n")
#print(users.get_user_info('john doe'))
#users.change()
#print(users.get_user_id('me'))