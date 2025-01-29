import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_growth_projection(initial_users, growth_rate, months, tier_limits, tier_prices, final_tier_price, use_tiers):
    users = [initial_users]
    for _ in range(months):
        users.append(int(users[-1] * (1 + growth_rate / 100)))
    
    pricing_data = []
    for i, user_count in enumerate(users):
        tier_costs = []
        remaining_users = user_count
        total_cost = 0
        if use_tiers:
            for limit, price in zip(tier_limits, tier_prices):
                if remaining_users > limit:
                    tier_cost = limit * price
                    remaining_users -= limit
                else:
                    tier_cost = remaining_users * price
                    remaining_users = 0
                tier_costs.append(tier_cost)
                total_cost += tier_cost
            
            if remaining_users > 0:
                final_tier_cost = remaining_users * final_tier_price
                total_cost += final_tier_cost
                tier_costs.append(final_tier_cost)
            else:
                tier_costs.append(0)
        else:
            final_tier_cost = user_count * final_tier_price
            total_cost = final_tier_cost
            tier_costs.append(final_tier_cost)
        
        pricing_data.append([i, user_count] + tier_costs + [total_cost])
    
    column_headers = ["Month", "Projected Users"]
    if use_tiers:
        column_headers += [f"Tier {i+1} Pricing ($)" for i in range(len(tier_limits))] + ["Final Tier Pricing ($)"]
    else:
        column_headers += ["Final Tier Pricing ($)"]
    column_headers.append("Total Estimated Pricing ($)")
    
    df = pd.DataFrame(pricing_data, columns=column_headers)
    return df

def plot_growth_projection(df, use_tiers):
    fig, ax = plt.subplots()
    months = df["Month"].astype(int)
    total_pricing = df["Total Estimated Pricing ($)"].astype(float)
    
    ax.plot(months, total_pricing, marker="o", linestyle="-", color="blue", label="Total Pricing")
    
    if use_tiers:
        colors = ["lightgreen", "lightcoral", "lightskyblue", "lightgoldenrodyellow"]
        tier_columns = [col for col in df.columns if "Tier" in col and "Total" not in col]
        
        bottom_values = np.zeros(len(months))
        for i, tier_col in enumerate(tier_columns):
            tier_values = df[tier_col].astype(float)
            ax.fill_between(months, bottom_values, bottom_values + tier_values, color=colors[i], alpha=0.5, label=tier_col)
            bottom_values += tier_values
    
    ax.set_xlabel("Month")
    ax.set_ylabel("Estimated Pricing ($)")
    ax.set_title("Projected Growth & Pricing")
    ax.legend()
    return fig

def main():
    st.title("Growth Projection Tool")
    
    st.sidebar.header("User Growth Settings")
    initial_users = st.sidebar.number_input("Initial Connected Users", value=10000, min_value=1)
    growth_rate = st.sidebar.number_input("Monthly Growth Rate (%)", value=5.0, min_value=0.0)
    months = st.sidebar.radio("Projection Period", [12, 24], index=0)
    
    use_tiers = st.sidebar.checkbox("Use Tiered Pricing", value=False)
    if use_tiers:
        num_tiers = st.sidebar.number_input("Number of Defined Tiers (Final Tier is Unbounded)", min_value=1, max_value=3, value=2)
        tier_limits = [st.sidebar.number_input(f"Tier {i+1} Limit", value=(i+1)*5000, min_value=1) for i in range(num_tiers)]
        tier_prices = [st.sidebar.number_input(f"Tier {i+1} Price", value=1.0, min_value=0.0) for i in range(num_tiers)]
        final_tier_price = st.sidebar.number_input("Final Tier Price (Applies to All Remaining Users)", value=0.80, min_value=0.0)
    else:
        tier_limits = []
        tier_prices = []
        final_tier_price = st.sidebar.number_input("Flat Cost per User ($)", value=1.0, min_value=0.0)
    
    df = generate_growth_projection(initial_users, growth_rate, months, tier_limits, tier_prices, final_tier_price, use_tiers)
    st.write("## Projected Growth & Pricing")
    df_display = df.copy()
    df_display.iloc[:, 2:] = df_display.iloc[:, 2:].applymap(lambda x: f"{x:.2f}")  # Format for display only
    st.dataframe(df_display)
    
    fig = plot_growth_projection(df, use_tiers)
    st.pyplot(fig)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "growth_projection.csv", "text/csv")
    st.download_button("Download Graph", "", "growth_projection.png", "image/png", key="graph_download")

if __name__ == "__main__":
    main()