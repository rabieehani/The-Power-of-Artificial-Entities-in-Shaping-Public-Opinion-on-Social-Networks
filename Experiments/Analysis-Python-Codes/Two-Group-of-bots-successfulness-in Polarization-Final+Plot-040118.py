import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import matplotlib.pyplot as plt
import re


def extract_number(condition_str):
    numbers = re.findall(r'\d+', condition_str)
    return int(numbers[0]) if numbers else 0  # تغییر به int برای حذف اعشار


def process_data(file_path, artificial_entity_median_input_1, artificial_entity_median_input_2):
    data = []
    time_steps = []
    run_ids = []
    additional_columns = {}
    opinion_medians_convergence = []
    opinion_medians_polarization = []
    conditions_for_plot = []
    clusters_data = {}

    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        lines = list(reader)
        column_names = [name.strip() for name in lines[6]]

        start_index = 2
        step_column = '[step]'
        if step_column not in column_names:
            raise ValueError(f"Column '{step_column}' not found.")

        end_index = column_names.index(step_column)
        additional_column_names = column_names[start_index:end_index]

        for col in additional_column_names:
            additional_columns[col] = []

        for i, line in enumerate(lines[7:]):
            run_ids.append(int(line[1]))
            for j, col in enumerate(additional_column_names):
                additional_columns[col].append(line[start_index + j].strip())
            time_steps.append(line[end_index].strip())
            numeric_values = [float(v.strip()) if v.strip() else np.nan for v in line[end_index + 1:]]
            data.append(numeric_values)

    data_df = pd.DataFrame(data)
    data_df['Run ID'] = run_ids[:len(data_df)]
    data_df['Time Step'] = time_steps[:len(data_df)]

    for col in additional_column_names:
        data_df[col] = additional_columns[col][:len(data_df)]

    group_columns = additional_column_names
    grouped_by_condition = data_df.groupby(group_columns)

    conditions = []
    convergence_rates = []
    polarization_rates = []
    divergence_rates = []
    success_rates_1 = []
    success_rates_2 = []

    for condition, group in grouped_by_condition:
        condition_str = ', '.join(f"{col}: {val}" for col, val in zip(group_columns, condition))
        conditions_for_plot.append(condition_str)

        grouped_by_run = group.groupby('Run ID')
        convergence_count = 0
        polarization_count = 0
        divergence_count = 0
        success_count_1 = 0
        success_count_2 = 0
        total_runs = len(grouped_by_run)

        for run_id, run_group in grouped_by_run:
            last_time_step = run_group['Time Step'].max()
            last_time_step_data = run_group[run_group['Time Step'] == last_time_step]
            last_time_step_data_clean = last_time_step_data.dropna(axis=1)

            if last_time_step_data_clean.empty or last_time_step_data_clean.shape[1] <= 2:
                continue

            opinions = last_time_step_data_clean.iloc[:, :-2].values.flatten()
            opinions_df = pd.DataFrame(opinions, columns=['Opinion'])
            overall_median_opinion = opinions_df['Opinion'].median()

            # بررسی موفقیت گروه‌ها
            threshold = 0.2
            if artificial_entity_median_input_1 - threshold <= overall_median_opinion <= artificial_entity_median_input_1 + threshold:
                success_count_1 += 1
            if -1 <= artificial_entity_median_input_2 <= 1:
                if artificial_entity_median_input_2 - threshold <= overall_median_opinion <= artificial_entity_median_input_2 + threshold:
                    success_count_2 += 1

            scaler = StandardScaler()
            opinions_scaled = scaler.fit_transform(opinions_df)
            dbscan = DBSCAN(eps=0.05, min_samples=40)
            clusters = dbscan.fit_predict(opinions_scaled)
            unique_clusters = set(clusters) - {-1}

            cluster_sizes = [len(opinions_df[clusters == c]) for c in unique_clusters]
            largest_cluster_size = max(cluster_sizes, default=0)
            largest_cluster_ratio = largest_cluster_size / len(opinions_df)

            # تشخیص نوع حالت
            is_convergence = False
            is_polarization = False

            if largest_cluster_ratio > 0.50:
                cluster_sizes_sorted = sorted(cluster_sizes, reverse=True)
                if len(cluster_sizes_sorted) >= 2:
                    absolute_difference_ratio = (cluster_sizes_sorted[0] - cluster_sizes_sorted[1]) / len(opinions_df)
                    is_convergence = absolute_difference_ratio >= 0.20
                else:
                    is_convergence = True

            if not is_convergence and len(unique_clusters) >= 2:
                is_polarization = all(len(opinions_df[clusters == c]) / len(opinions_df) >= 0.10
                                      for c in unique_clusters)

            is_divergence = not (is_convergence or is_polarization)

            # شمارش وضعیت‌ها
            if is_convergence:
                convergence_count += 1
                opinion_medians_convergence.append(overall_median_opinion)
            elif is_polarization:
                polarization_count += 1
                opinion_medians_polarization.append(overall_median_opinion)
            else:
                divergence_count += 1

            # ذخیره اطلاعات خوشه‌ها
            clusters_data[condition_str] = []
            for cluster in unique_clusters:
                cluster_opinions = opinions_df[clusters == cluster]
                clusters_data[condition_str].append({
                    'median': cluster_opinions['Opinion'].median(),
                    'size': len(cluster_opinions),
                    'opinions': cluster_opinions['Opinion'].tolist(),
                    'is_convergence': is_convergence,
                    'is_polarization': is_polarization
                })

        # محاسبه نرخ‌ها
        convergence_rate = (convergence_count / total_runs) * 100
        polarization_rate = (polarization_count / total_runs) * 100
        divergence_rate = (divergence_count / total_runs) * 100
        success_rate_1 = (success_count_1 / total_runs) * 100
        success_rate_2 = (success_count_2 / total_runs) * 100 if -1 <= artificial_entity_median_input_2 <= 1 else 0

        conditions.append(condition_str)
        convergence_rates.append(convergence_rate)
        polarization_rates.append(polarization_rate)
        divergence_rates.append(divergence_rate)
        success_rates_1.append(success_rate_1)
        success_rates_2.append(success_rate_2)

    # استخراج نرخ جمعیت گروه دوم از نام شرایط (اعداد صحیح)
    population_ratios = [f"{extract_number(cond)}/10" for cond in conditions]

    # مرتب‌سازی بر اساس نرخ جمعیت گروه دوم
    sorted_indices = np.argsort([extract_number(cond) for cond in conditions])
    population_ratios = [population_ratios[i] for i in sorted_indices]
    convergence_rates = [convergence_rates[i] for i in sorted_indices]
    polarization_rates = [polarization_rates[i] for i in sorted_indices]
    divergence_rates = [divergence_rates[i] for i in sorted_indices]
    success_rates_1 = [success_rates_1[i] for i in sorted_indices]
    success_rates_2 = [success_rates_2[i] for i in sorted_indices]

    # نمایش نتایج
    print("\nSummary Statistics:")
    print(f"Convergence: {np.mean(convergence_rates):.1f}%")
    print(f"Polarization: {np.mean(polarization_rates):.1f}%")
    print(f"Divergence: {np.mean(divergence_rates):.1f}%")

    # رسم نمودارها با تغییرات درخواستی
    plot_public_opinion(population_ratios, convergence_rates, polarization_rates, divergence_rates)
    plot_success_rates(population_ratios, success_rates_1, success_rates_2)
    plot_opinion_distribution_with_clusters(
        population_ratios, opinion_medians_convergence, opinion_medians_polarization,
        artificial_entity_median_input_1, artificial_entity_median_input_2,
        clusters_data, len(data_df)
    )


def plot_public_opinion(population_ratios, convergence_rates, polarization_rates, divergence_rates):
    plt.figure(figsize=(12, 6))
    x = range(len(population_ratios))

    plt.plot(x, convergence_rates, label="Convergence", marker='o', color='blue')
    plt.plot(x, polarization_rates, label="Polarization", marker='s', color='red')
    plt.plot(x, divergence_rates, label="Divergence", marker='^', color='green')

    plt.xlabel("The population ratio of the second group to the first group", fontsize=12)
    plt.ylabel("Probability (%)", fontsize=12)
    plt.xticks(x, population_ratios, rotation=45)
    plt.legend(loc='center right')  # تغییر موقعیت راهنما به سمت راست وسط
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_success_rates(population_ratios, success_rates_1, success_rates_2):
    plt.figure(figsize=(12, 6))
    x = range(len(population_ratios))

    # تغییر رنگ‌ها و برچسب‌ها مطابق درخواست
    plt.plot(x, success_rates_1, label="First Group (Larger but dumb)", marker='o', color='red')
    plt.plot(x, success_rates_2, label="Second Group (Smaller but smart)", marker='s', color='blue')

    plt.xlabel("The population ratio of the second group to the first group", fontsize=12)
    plt.ylabel("Success Rate (%)", fontsize=12)
    plt.xticks(x, population_ratios, rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_opinion_distribution_with_clusters(
        population_ratios,
        opinion_medians_convergence,
        opinion_medians_polarization,
        artificial_entity_median_1,
        artificial_entity_median_2,
        clusters_data,
        total_users
):
    plt.figure(figsize=(14, 7))
    plt.ylim(-1, 1)
    plt.axhline(0, color='gray', linestyle='--', alpha=0.3)

    # محاسبه درصد هر حالت
    convergence_percent = len(opinion_medians_convergence) / len(population_ratios) * 100
    polarization_percent = len(opinion_medians_polarization) / len(population_ratios) * 100
    divergence_percent = 100 - convergence_percent - polarization_percent

    # ایجاد عناصر برای راهنما
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label=f'Consensus ({convergence_percent:.1f}%)',
                   markerfacecolor='blue', markersize=10),
        plt.Line2D([0], [0], marker='s', color='w', label=f'Polarization ({polarization_percent:.1f}%)',
                   markerfacecolor='red', markersize=10),
        plt.Line2D([0], [0], marker='^', color='w', label=f'Divergence ({divergence_percent:.1f}%)',
                   markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], color='darkred', linestyle=':', label='Group 1 Target'),
        plt.Line2D([0], [0], color='darkgreen', linestyle=':', label='Group 2 Target')
    ]

    for i, ratio in enumerate(population_ratios):
        condition_str = f"Population ratio: {ratio}"  # ساخت رشته شرط برای جستجو در clusters_data
        if condition_str in clusters_data:
            clusters = clusters_data[condition_str]
            sorted_clusters = sorted(clusters, key=lambda x: x['size'], reverse=True)

            # تعیین نوع حالت
            if ratio in [r for r, _ in zip(population_ratios, opinion_medians_convergence)]:
                condition_type = "convergence"
            elif ratio in [r for r, _ in zip(population_ratios, opinion_medians_polarization)]:
                condition_type = "polarization"
            else:
                condition_type = "divergence"

            # نمایش کلاسترها
            for j, cluster in enumerate(sorted_clusters):
                cluster_ratio = cluster['size'] / total_users
                if cluster_ratio < 0.1 and j > 0:  # فقط بزرگترین کلاستر اگر کوچک باشد
                    continue

                if condition_type == "convergence":
                    color = 'blue' if j == 0 else 'lightblue'
                    marker = 'o'
                elif condition_type == "polarization":
                    color = 'red'
                    marker = 's'
                else:
                    color = 'green'
                    marker = '^'

                plt.scatter(i, cluster['median'], s=cluster['size'] * 2,
                            color=color, marker=marker, alpha=0.7, edgecolors='black')
                plt.text(i, cluster['median'], f"{cluster['median']:.2f}",
                         ha='center', va='center', fontsize=8)

    # خطوط هدف
    plt.axhline(y=artificial_entity_median_1, color='darkred', linestyle=':')
    plt.axhline(y=artificial_entity_median_2, color='darkgreen', linestyle=':')

    plt.xlabel("The population ratio of the second group to the first group", fontsize=12)
    plt.ylabel("Opinion Value", fontsize=12)
    plt.title("Opinion Distribution by Population Ratio", fontsize=14)
    plt.xticks(range(len(population_ratios)), population_ratios, rotation=45)

    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def get_user_input():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return None, None, None

    # ایجاد متغیرهای برای ذخیره مقادیر ورودی
    median1 = None
    median2 = None

    # ایجاد پنجره ورودی
    input_window = tk.Toplevel(root)
    input_window.title("Input Parameters")

    tk.Label(input_window, text="Group 1 Target Median:").pack()
    entry1 = tk.Entry(input_window)
    entry1.pack()

    tk.Label(input_window, text="Group 2 Target Median (or 2 if N/A):").pack()
    entry2 = tk.Entry(input_window)
    entry2.pack()

    def on_submit():
        nonlocal median1, median2
        try:
            median1 = float(entry1.get())
            median2 = float(entry2.get())
            input_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    tk.Button(input_window, text="Submit", command=on_submit).pack()

    input_window.wait_window()
    root.destroy()

    return file_path, median1, median2


def main():
    file_path, median1, median2 = get_user_input()
    if file_path and median1 is not None and median2 is not None:
        process_data(file_path, median1, median2)


if __name__ == "__main__":
    main()
