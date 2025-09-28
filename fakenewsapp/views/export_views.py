import io
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from ..models import NewsCheck
from fakenewsapp.models import NewsCheck


@login_required
def export_dashboard_csv(request):
    # Create response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dashboard_report.csv"'

    writer = csv.writer(response)

    # ✅ Add a title row
    writer.writerow(["Fake News Detection & Visualization System"])
    writer.writerow(["Dashboard Report"])
    writer.writerow([])  # empty line for spacing

    # ✅ Add column headers (clean)
    writer.writerow(["Title", "Prediction", "Confidence (%)", "Date Checked"])

    # ✅ Query logs
    checks = NewsCheck.objects.filter(user=request.user).order_by('-date_checked')


    for check in checks:
        writer.writerow([
            check.news_title,
            check.prediction,
            f"{round(check.probability, 2)}%" if check.probability else "N/A",
            f'"{check.date_checked.strftime("%Y-%m-%d %H:%M")}"' if check.date_checked else "N/A",
        ])

    # ✅ Add a footer row
    writer.writerow([])
    writer.writerow(["Report generated from Fake News Detection Dashboard"])

    return response


@login_required
def export_dashboard_pdf(request):
    # Query data
    lifecycle_data = request.session.get("lifecycle_data", {})
    risk_trend = request.session.get("risk_trend", [])
    checks = NewsCheck.objects.filter(user=request.user).order_by("-date_checked")

    total_checks = checks.count()
    fake_count = checks.filter(prediction="FAKE").count()
    real_count = checks.filter(prediction="REAL").count()

    # Response setup
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="dashboard_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=9)

    # Title
    elements.append(Paragraph("📊 Fake News Dashboard Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    # Summary
    summary_text = (
        f"Report generated on <b>{now().strftime('%Y-%m-%d %H:%M')}</b><br/><br/>"
        f"You checked <b>{total_checks}</b> news items. "
        f"<b>{fake_count}</b> were <font color='red'>FAKE</font>, "
        f"<b>{real_count}</b> were <font color='green'>REAL</font>."
    )
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Chart helper
    def add_chart(fig, title=""):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img = RLImage(buf, width=400, height=250)
        if title:
            elements.append(Paragraph(title, styles["Heading3"]))
        elements.append(img)
        elements.append(Spacer(1, 20))
        plt.close(fig)

    # 1. Fake vs Real
    fig, ax = plt.subplots()
    if total_checks > 0:
        ax.pie([real_count, fake_count], labels=["Real", "Fake"], autopct="%1.1f%%",
               colors=["#28a745", "#dc3545"])
    else:
        ax.text(0.5, 0.5, "No Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Fake vs Real News Distribution")

    # 2. Checks Over Time (last 7 days)
    last_7_days = now() - timedelta(days=7)
    trend_data = (
        checks.filter(date_checked__gte=last_7_days)
        .annotate(day=TruncDate("date_checked"))
        .values("day")
        .annotate(
            fake=Count("id", filter=Q(prediction="FAKE")),
            real=Count("id", filter=Q(prediction="REAL")),
        )
        .order_by("day")
    )
    
    fig, ax = plt.subplots()
    if trend_data:
        days = [d["day"] for d in trend_data]
        totals = [d["fake"] + d["real"] for d in trend_data]
        ax.plot(days, totals, marker="o", color="#007bff")
        ax.set_xlabel("Date"); ax.set_ylabel("Total Checks")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.autofmt_xdate(rotation=45)
    else:
        ax.text(0.5, 0.5, "No Trend Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "News Checks Over Time (Last 7 Days)")

    # 3. Language-wise Fake vs Real
    lang_data = checks.values("language", "prediction").annotate(total=Count("id"))
    fig, ax = plt.subplots()
    if lang_data:
        langs = list(set([d["language"] for d in lang_data]))
        fake_vals = [sum(d["total"] for d in lang_data if d["language"] == l and d["prediction"] == "FAKE") for l in langs]
        real_vals = [sum(d["total"] for d in lang_data if d["language"] == l and d["prediction"] == "REAL") for l in langs]
        ax.bar(langs, fake_vals, label="Fake", color="#dc3545")
        ax.bar(langs, real_vals, bottom=fake_vals, label="Real", color="#28a745")
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No Language Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Language-wise Fake vs Real")

    # 4. Confidence Radar (bucketed ranges)
    probs = [c.probability for c in checks if c.probability]
    buckets = {"50-60": 0, "60-70": 0, "70-80": 0, "80-90": 0, "90-100": 0}
    for p in probs:
        if 50 <= p < 60: buckets["50-60"] += 1
        elif 60 <= p < 70: buckets["60-70"] += 1
        elif 70 <= p < 80: buckets["70-80"] += 1
        elif 80 <= p < 90: buckets["80-90"] += 1
        elif 90 <= p <= 100: buckets["90-100"] += 1
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    if probs:
        labels = list(buckets.keys())
        values = list(buckets.values())
        values += values[:1]
        angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
        angles += angles[:1]
        ax.plot(angles, values, "o-", color="#36a2eb")
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
    else:
        ax.text(0.5, 0.5, "No Confidence Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Confidence Level Distribution")

    # 5. Weekly Fake vs Real (stacked bar)
    fig, ax = plt.subplots()
    if trend_data:
        days = [d["day"] for d in trend_data]
        fakes = [d["fake"] for d in trend_data]
        reals = [d["real"] for d in trend_data]
        ax.bar(days, fakes, label="Fake", color="#dc3545")
        ax.bar(days, reals, bottom=fakes, label="Real", color="#28a745")
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.autofmt_xdate(rotation=45)
    else:
        ax.text(0.5, 0.5, "No Weekly Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Weekly Fake vs Real Trend")

    # 6. Fake News Lifecycle Radar
    lifecycle_labels = ["Creation", "Initial_Spread", "Peak_Reach", "Detection", "Correction", "Residual_Impact"]
    lifecycle_values = [lifecycle_data.get(k, 0) for k in lifecycle_labels]

    # Separate pretty labels for chart display
    chart_labels = ["Creation", "Initial Spread", "Peak Reach", "Detection", "Correction", "Residual Impact"]

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    if any(lifecycle_values):
        lifecycle_values += lifecycle_values[:1]
        angles = [n / float(len(lifecycle_labels)) * 2 * 3.14159 for n in range(len(lifecycle_labels))]
        angles += angles[:1]
        ax.plot(angles, lifecycle_values, "o-", color="#ff6384")
        ax.fill(angles, lifecycle_values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(chart_labels)
        ax.set_ylim(0, 100) 
    else:
        ax.text(0.5, 0.5, "No Lifecycle Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Fake News Lifecycle Radar")

    # Lifecycle Table
    data = [["Stage", "Strength (%)"]] + [[s, str(v)] for s, v in lifecycle_data.items()]
    lifecycle_table = Table(data, hAlign="LEFT")
    lifecycle_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(lifecycle_table)
    elements.append(Spacer(1, 20))

    # 7. Risk Trend (line)
    fig, ax = plt.subplots()
    if risk_trend:
        ax.plot([r["day"] for r in risk_trend], [r["risk"] for r in risk_trend],
                marker="o", color="#dc3545")
        ax.set_ylim(0, 100)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.autofmt_xdate(rotation=45)
    else:
        ax.text(0.5, 0.5, "No Risk Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Fake News Risk Trend (7 Days)")

    # 8. Confidence Spread (bar)
    fig, ax = plt.subplots()
    if trend_data:
        ax.bar([d["day"] for d in trend_data], [d["fake"] + d["real"] for d in trend_data],
               color="#007bff")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.autofmt_xdate(rotation=45)
    else:
        ax.text(0.5, 0.5, "No Spread Data", ha="center", va="center")
        ax.axis("off")
    add_chart(fig, "Prediction Confidence Spread")

    # 9. Recent Alerts Table
    data = [["Title", "Prediction", "Confidence", "Date"]]
    for check in checks[:10]:
        data.append([
            Paragraph(check.news_title, wrap_style),
            check.prediction,
            f"{check.probability:.2f}%" if check.probability else "N/A",
            check.date_checked.strftime("%Y-%m-%d %H:%M") if check.date_checked else "N/A",
        ])
    alerts_table = Table(data, hAlign="LEFT", colWidths=[200, 60, 60, 100])
    alerts_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(Paragraph(" Real-Time Detection Alerts", styles["Heading2"]))
    elements.append(alerts_table)

    # Build PDF
    doc.build(elements)
    return response
