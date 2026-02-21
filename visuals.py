import plotly.express as px
import pandas as pd

def generate_visuals(df):
    """Generates a list of plotly figures and their interpretations based on the data."""
    figures = []
    
    numeric_df = df.select_dtypes(include=['number'])
    cat_df = df.select_dtypes(include=['object', 'category'])
    
    # 1. Correlation Heatmap
    if numeric_df.shape[1] > 1:
        corr = numeric_df.corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="Tealgrn",
                             title="Correlation Heatmap")
        interpretation = "This chart shows how different numbers in your data relate to each other. It works like a color-coded map where strong, bright colors indicate that two variables strongly affect each other—for example, as one goes up, the other might consistently go up or down too. On the other hand, faded or dark colors mean there is little to no connection between those specific numbers. You can use this to quickly spot hidden patterns and figure out which factors carry the most weight in your dataset."
        figures.append({"type": "heatmap", "fig": fig_corr, "interpretation": interpretation})
        
        # Find highest correlation
        corr_unstacked = corr.abs().unstack()
        corr_unstacked = corr_unstacked[corr_unstacked < 1]
    
    # 2. Histogram
    if not numeric_df.empty:
        target_col = numeric_df.var().idxmax()
        fig_hist = px.histogram(df, x=target_col, nbins=30, marginal="box",
                                color_discrete_sequence=['#00e6ff'],
                                title=f"Distribution of {target_col}")
        interpretation = f"This chart shows how the values for '{target_col}' are spread out across your entire dataset. The tall bars act like a popularity contest, showing you the most common and frequent values at a glance. Just above or below the bars, the small box-like shape helps you spot any unusual, extreme values that don't quite fit the normal pattern. This is especially helpful if you want to understand what a 'typical' number looks like versus an unexpected outlier."
        figures.append({"type": "histogram", "fig": fig_hist, "interpretation": interpretation})
        
    # 3. Scatter plot
    if numeric_df.shape[1] > 1 and 'corr_unstacked' in locals() and not corr_unstacked.empty:
        max_corr_idx = corr_unstacked.idxmax()
        col1, col2 = max_corr_idx
        try:
            fig_scatter = px.scatter(df, x=col1, y=col2, trendline="ols",
                                     color_discrete_sequence=['#ff4b4b'],
                                     title=f"Scatter Plot: {col1} vs {col2}")
        except ImportError:
             fig_scatter = px.scatter(df, x=col1, y=col2,
                                     color_discrete_sequence=['#ff4b4b'],
                                     title=f"Scatter Plot: {col1} vs {col2}")
        interpretation = f"This chart plots '{col1}' against '{col2}' to show their direct relationship. Each dot represents a single piece of data, and by looking at how the dots are scattered, you can see if the two variables generally move together. The straight line drawn through the middle illustrates the overall trend—whether they usually go up or down in tandem. If the dots are tightly packed around the line, the relationship is very strong."
        figures.append({"type": "scatter", "fig": fig_scatter, "interpretation": interpretation})

    # 4. Box Plot (Multiple numerical columns)
    if numeric_df.shape[1] > 0:
        cols_to_plot = numeric_df.columns[:5] # Limit to 5 for readability
        mdf = pd.melt(df[cols_to_plot])
        fig_box = px.box(mdf, x="variable", y="value", color="variable",
                         title="Distribution Comparison (Box Plot)")
        interpretation = "These boxes provide a direct comparison between different numerical columns in your data. For each box, the line drawn right through the middle represents the 'typical' or median value. The colored box itself holds the vast majority of your typical data points, while any dots floating far away represent unusual, extreme values. This makes it incredibly easy to see which variables have a wide range of unpredictable numbers and which ones are tightly grouped together."
        figures.append({"type": "box", "fig": fig_box, "interpretation": interpretation})

    # 5. Bar Chart
    if not cat_df.empty:
        nunique = cat_df.nunique()
        valid_cat_cols = nunique[(nunique > 1) & (nunique <= 20)]
        if not valid_cat_cols.empty:
            target_cat = valid_cat_cols.idxmax()
            val_counts = df[target_cat].value_counts().reset_index()
            val_counts.columns = [target_cat, 'Count']
            fig_bar = px.bar(val_counts, x=target_cat, y='Count',
                             color=target_cat,
                             title=f"Frequency of Categories in {target_cat}")
            interpretation = f"This bar chart counts how often each specific category appears within the '{target_cat}' group. It acts as a visual simple tally, making it incredibly clear to see which categories are the most popular and which are the rarest. By comparing the heights of the bars side-by-side, you can immediately identify the dominant groups within your data without getting bogged down by raw numbers and percentages."
            figures.append({"type": "bar", "fig": fig_bar, "interpretation": interpretation})

    # 6. Pie Chart
    if not cat_df.empty:
        nunique = cat_df.nunique()
        valid_pie_cols = nunique[(nunique > 1) & (nunique <= 5)]
        if not valid_pie_cols.empty:
            pie_cat = valid_pie_cols.idxmin()
            val_counts = df[pie_cat].value_counts().reset_index()
            val_counts.columns = [pie_cat, 'Count']
            fig_pie = px.pie(val_counts, names=pie_cat, values='Count',
                             title=f"Proportion of Categories in {pie_cat}", hole=0.3)
            interpretation = f"This circular ring chart shows the overall makeup of '{pie_cat}'. It helps you quickly see what 'piece of the pie' each individual category takes up out of the entire whole. Visualizing data this way is perfect for understanding relative sizes and proportions at a glance, allowing you to instantly realize if one specific group dominates the rest or if everything is split relatively evenly."
            figures.append({"type": "pie", "fig": fig_pie, "interpretation": interpretation})

    # 7. Violin Plot
    if numeric_df.shape[1] > 0:
        target_col_violin = numeric_df.columns[min(1, len(numeric_df.columns)-1)]
        fig_violin = px.violin(df, y=target_col_violin, box=True, points="all",
                               title=f"Violin Plot of {target_col_violin}", color_discrete_sequence=['#a5ffd6'])
        interpretation = f"This unique 'violin' shape shows exactly where the values for '{target_col_violin}' are most concentrated. Instead of just a colored box, thicker and wider areas of the shape mean that a large number of data points are clustered very tightly around those specific values. Thinner areas mean those numbers are much rarer. It is an excellent way to see the true 'shape' of your data, including whether it favors high numbers, low numbers, or is balanced in the middle."
        figures.append({"type": "violin", "fig": fig_violin, "interpretation": interpretation})

    # 8. Line Chart
    if numeric_df.shape[1] > 0:
        target_col_line = numeric_df.columns[0]
        fig_line = px.line(df.reset_index(), x='index', y=target_col_line, 
                           title=f"Trend of {target_col_line} over Data Range")
        interpretation = f"This line tracks exactly how the numbers for '{target_col_line}' change sequentially from start to finish. It is essentially drawing a path through your data points from left to right. This makes it a fantastic tool for spotting overall, big-picture trends over time or sequence. By following the peaks and valleys of the line, you can quickly tell whether the numbers are generally rising, falling steadily, or experiencing wild fluctuations."
        figures.append({"type": "line", "fig": fig_line, "interpretation": interpretation})

    # 9. Density Contour Plot
    if numeric_df.shape[1] > 1 and 'corr_unstacked' in locals() and not corr_unstacked.empty:
        max_corr_idx = corr_unstacked.idxmax()
        col1, col2 = max_corr_idx
        fig_contour = px.density_contour(df, x=col1, y=col2, title=f"Density Contour: {col1} vs {col2}")
        fig_contour.update_traces(contours_coloring="fill")
        interpretation = f"Think of this as a topographical map showing exactly where the data for '{col1}' and '{col2}' is the most crowded. The series of inner 'rings' or 'contours' highlight the most common and frequent combinations of these two variables. Areas with many tight rings indicate a massive cluster of similar data points. This helps you identify the 'sweet spot' or the most typical relationship pairing between these two different parts of your dataset."
        figures.append({"type": "contour", "fig": fig_contour, "interpretation": interpretation})

    return figures
