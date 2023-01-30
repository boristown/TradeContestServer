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