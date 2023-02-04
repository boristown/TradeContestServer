import pywebio.pin
import pywebio.output
import on_event

#交易选项行
#三列布局：30% auto 30%
def trade_options_row(left,middle,right):
    return pywebio.output.put_row(
        [
            left,
            middle,
            right
        ],
        size = f"30% auto 30%",
    )

#检测UI输入是否改变
def chain_changed(cli,changed,chain):
    for var in chain:
        if getattr(cli,var) != pywebio.pin.pin[var]:
            changed[var] = pywebio.pin.pin[var]

#默认零值的浮点数输入框
def float_input(id,readonly=False):
    print(dir(pywebio.pin))
    return pywebio.pin.put_input(id,type=FLOAT,value=0.0,placeholder='0.0',readonly=readonly)

def trade_conf_button(cli):
    print(dir(pywebio.pin))
    pywebio.pin.put_button('确认', onclick=lambda cli=cli:on_event.trade_confirm_click(cli), small=True)