import os
import json
import requests


def get_recommendations(metrics):
    net_profit = metrics.get("net_profit", 0)
    revenue = metrics.get("total_revenue", 0)
    expenses = metrics.get("total_expenditure", 0)
    cogs = metrics.get("cogs", 0)
    sales_total = metrics.get("sales_total", 0)
    outstanding_loans = metrics.get("outstanding_loans", 0)

    recommendations = []

    if revenue > 0:
        expense_ratio = expenses / revenue
        if expense_ratio > 0.75:
            recommendations.append("Expenses are high relative to income. Review recurring costs and cut non-essential spending.")
        elif expense_ratio < 0.5:
            recommendations.append("Your expense ratio looks healthy. Keep a reserve for slow periods and future growth.")

    if net_profit < 0:
        recommendations.append("Cash flow is currently negative. Prioritize essential spending and delay discretionary purchases.")
    elif net_profit > 0:
        recommendations.append("You are making a positive cash balance. Reserve part of the surplus for loan repayment or stock replenishment.")

    if outstanding_loans > 0:
        recommendations.append("You still have outstanding loans. Use part of the surplus to reduce interest pressure.")

    if sales_total > 0 and cogs > 0:
        gross_margin = (sales_total - cogs) / sales_total
        if gross_margin < 0.3:
            recommendations.append("Gross margin is tight. Revisit pricing or supplier costs to improve profit.")

    if not recommendations:
        recommendations.append("Your business looks stable. Keep tracking sales, expenses, and loan repayments weekly.")

    if len(recommendations) > 3:
        recommendations = recommendations[:3]

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            prompt = (
                "You are a business finance assistant. Give 3 concise recommendations for a small business owner based on these figures: "
                f"revenue={revenue}, expenses={expenses}, net_profit={net_profit}, sales={sales_total}, loan_balance={outstanding_loans}."
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3},
            }
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                json=payload,
                timeout=15,
            )
            if response.ok:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return [line.strip(" -") for line in text.splitlines() if line.strip()][:3]
        except Exception:
            pass

    return recommendations
