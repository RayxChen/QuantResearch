import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dowhy import CausalModel
from concurrent.futures import ProcessPoolExecutor
from data_preprocess import preprocess_data, load_config
import os

def process_treatment(treatment, df, outcome, common_causes):
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=common_causes
    )
    
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
    estimate = model.estimate_effect(identified_estimand, method_name="backdoor.linear_regression")
    print(estimate)
    refutation_methods = [
        "random_common_cause",
        "placebo_treatment_refuter",
        "data_subset_refuter",
        # "bootstrap_refuter"
    ]
    
    treatment_refutations = []
    for method in refutation_methods:
        refutation = model.refute_estimate(identified_estimand, estimate, method_name=method)
        treatment_refutations.append({
            'treatment': treatment,
            'refutation_type': method,
            'refuted_estimate': refutation.new_effect,
            'p_value': refutation.refutation_result.get('p_value')
        })
    
    return treatment, estimate, treatment_refutations

def perform_causal_inference(df, treatments, outcome, common_causes):
    results = {}
    all_refutations = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_treatment, treatment, df, outcome, common_causes) for treatment in treatments]
        for future in futures:
            treatment, estimate, treatment_refutations = future.result()
            results[treatment] = estimate
            all_refutations.extend(treatment_refutations)

    return results, all_refutations

def summarize_refutations(refutations, output_dir):
    refutations_df = pd.DataFrame(refutations)
    summary = refutations_df.groupby('refutation_type').agg({
        'refuted_estimate': ['mean', 'std'],
        'p_value': ['mean', 'std']
    })

    interpretation = f"\nInterpretation of Refutations:\n"
    
    for refutation_type, row in summary.iterrows():
        mean_estimate, std_estimate = row[('refuted_estimate', 'mean')], row[('refuted_estimate', 'std')]
        mean_p_value = row[('p_value', 'mean')]
        
        interpretation += f"\n{refutation_type.replace('_', ' ').title()}:\n"
        interpretation += f"  - Mean refuted estimate: {mean_estimate:.6f} (std: {std_estimate:.6f})\n"
        interpretation += f"  - Mean p-value: {mean_p_value:.3f}\n"
        
        if abs(mean_estimate) < 0.001 and mean_p_value > 0.05:
            interpretation += "  - Interpretation: This refutation supports the robustness of the original results.\n"
        elif abs(mean_estimate) >= 0.001 or mean_p_value <= 0.05:
            interpretation += "  - Interpretation: This refutation suggests some sensitivity in the original results.\n"
        else:
            interpretation += "  - Interpretation: Results are inconclusive, further investigation may be needed.\n"
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'refutation.txt')
    with open(output_file, 'w') as f:
        f.write(interpretation)
    
    return summary, interpretation

def plot_causal_effects(results, treatments, config, research_topic):
    effect_sizes = [results[t].value * 100 for t in treatments]
    confidence_intervals = [
        [ci * 100 for ci in results[t].get_confidence_intervals()[0]] for t in treatments
    ]
    # plt.style.use('ggplot')
    plt.figure(figsize=(12, 8))
    x = range(len(treatments))
    # colors = plt.cm.tab10(np.linspace(0, 1, len(treatments)))
    colors = plt.cm.viridis(np.linspace(0, 1, len(treatments)))

    bars = plt.bar(x, effect_sizes, color=colors, alpha=0.7, width=0.6)

    plt.errorbar(x, effect_sizes, 
                 yerr=[[v - e[0] for e, v in zip(confidence_intervals, effect_sizes)],
                       [e[1] - v for e, v in zip(confidence_intervals, effect_sizes)]],
                 fmt='none', capsize=5, color='black', elinewidth=2, alpha=0.7)

    outcome = config['research_topics'][research_topic]['outcome'][0]
    plt.title(f"Causal Effect on {outcome.replace('_', ' ').title()}", fontsize=18, fontweight='bold')
    plt.xlabel("Treatment", fontsize=14)
    plt.ylabel(f"{outcome.replace('_', ' ').title()} Change (%)", fontsize=14)
    plt.xticks(x, treatments, fontsize=12, rotation=45, ha='right')
    plt.yticks(fontsize=12)

    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.2f}'.format(y)))

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}%',
                 ha='center', va='bottom', fontsize=12)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(['Effect Size'], loc='upper right', fontsize=12)
    plt.tight_layout()

    output_dir = config['research_topics'][research_topic]['output_directory']
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{research_topic}.jpg')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    config = load_config('config.yaml')
    research_topic = 'weekday_effect'  # change this to other topics from the config
    
    outcome = config['research_topics'][research_topic]['outcome'][0]  # Fixed: Use the outcome from config
    df, treatments, common_causes = preprocess_data('your_data.csv', config, research_topic, outcome)
    
    output_dir = config['research_topics'][research_topic].get('output_directory', 'output')  # Fixed: Use the output directory from config
    os.makedirs(output_dir, exist_ok=True)

    results, refutations = perform_causal_inference(df, treatments, outcome, common_causes)
    
    refutation_summary, interpretation = summarize_refutations(refutations, output_dir)

    plot_causal_effects(results, treatments, config, research_topic)

if __name__ == "__main__":
    main()
