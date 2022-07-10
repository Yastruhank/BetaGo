from core.load_param import app,saya,channel_list,modules_list

with saya.module_context():
    for module in modules_list:
        channel_list[module] = saya.require(module)
    


app.launch_blocking()