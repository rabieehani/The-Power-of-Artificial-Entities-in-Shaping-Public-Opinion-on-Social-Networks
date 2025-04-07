import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import tkinter as tk
from tkinter import filedialog, messagebox


def plot_combined_success_chart(file_path, legend_pos):
    # خواندن داده‌ها از فایل
    data = pd.read_excel(file_path, header=None)

    # خواندن معیار اصلی از سلول A1
    primary_metric = data.iloc[0, 0]

    # نرخ‌های بات (محور X)
    bot_rates = data.iloc[0, 1:].astype(float) * 100

    # مقادیر موفقیت و استراتژی‌ها
    success_values = data.iloc[1:, 1:]
    strategies = data.iloc[1:, 0].values

    # لیست الگوهای خط
    line_styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1))]

    # رسم نمودار
    plt.figure(figsize=(12, 6))
    for i, strategy in enumerate(strategies):
        plt.plot(
            bot_rates,
            success_values.iloc[i] * 100,
            marker='o',
            linestyle=line_styles[i % len(line_styles)],
            label=f"{strategy}"
        )

    # تنظیمات نمودار
    plt.xlabel("Artificial Entity Population Rate (%)", fontsize=12)
    plt.ylabel("Success Rate (%)", fontsize=12)

    # فرمت درصدی محورها
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}%'))
    plt.xticks(bot_rates)

    # تعیین مکان راهنما بر اساس انتخاب کاربر
    if legend_pos == "top_left":
        legend_loc = 'upper left'
        bbox_anchor = (0.0, 1.0)  # بالا سمت چپ
    else:
        legend_loc = 'lower right'
        bbox_anchor = (1.0, 0.0)  # پایین سمت راست

    plt.legend(
        title=f"{primary_metric}",
        loc=legend_loc,
        bbox_to_anchor=bbox_anchor
    )

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


def main():
    # دریافت مسیر فایل
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select the Excel file",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not file_path:
        print("No file selected.")
        return

    # ایجاد پنجره انتخاب مکان راهنما
    root = tk.Tk()
    root.withdraw()
    legend_pos = messagebox.askquestion(
        "Legend Position",
        "Do you want the legend in top left? (No for bottom right)",
        icon='question'
    )

    # تبدیل پاسخ به مقدار قابل استفاده
    legend_pos = "top_left" if legend_pos == 'yes' else "bottom_right"

    # رسم نمودار با موقعیت انتخابی
    plot_combined_success_chart(file_path, legend_pos)


if __name__ == "__main__":
    main()