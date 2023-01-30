import pywebio.pin
import pywebio.output

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