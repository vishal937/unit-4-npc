#!/usr/bin/env python3
"""
==============================================================================
NPC Unit 4 Assignment: Configure DHCP and Set Up a Network Using Cisco Packet Tracer
Academic PDF Report Generator
==============================================================================
Student Name   : Vishal Katyare
PRN Number     : 2125UCSM1034
Department     : Computer Science Engineering (Cyber Security)
Institution    : Sanjivani University, Kopargaon
Subject        : Network Protocols and Communication (NPC - Unit 4)
Academic Year  : 2026–2027
==============================================================================
"""

import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(HERE, "NPC_Unit4_DHCP_Assignment_Report.pdf")
SCREENSHOTS_DIR = os.path.join(HERE, "screenshots")

# Academic Color Palette
NAVY = HexColor(0x1F3864)       # Primary Headings
BLUE = HexColor(0x2E5496)       # Secondary Subheadings
DARK_TEXT = HexColor(0x222222)  # Charcoal Body Text
GREY = HexColor(0x595959)       # Accent Gray
LGREY = HexColor(0xD9D9D9)      # Borders & Dividers
ROWBG = HexColor(0xEEF2F9)      # Table Alternate Row
HDRBG = HexColor(0x1F3864)      # Table Header
CALLOUT_BG = HexColor(0xEFF6FF) # Light Blue Callout

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
CONTENT_W = PAGE_W - (2 * MARGIN)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for dynamic total page count, running headers, and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress on cover page

        self.saveState()
        # Header
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(BLUE)
        self.drawString(MARGIN, PAGE_H - 1.1 * cm, "SANJIVANI UNIVERSITY | DEPARTMENT OF COMPUTER SCIENCE ENGINEERING")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(GREY)
        self.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.1 * cm, "NPC Unit 4 — DHCP Configuration & Network Setup")

        self.setStrokeColor(LGREY)
        self.setLineWidth(0.6)
        self.line(MARGIN, PAGE_H - 1.25 * cm, PAGE_W - MARGIN, PAGE_H - 1.25 * cm)

        # Footer
        self.line(MARGIN, 1.25 * cm, PAGE_W - MARGIN, 1.25 * cm)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(GREY)
        self.drawString(MARGIN, 0.9 * cm, "Vishal Katyare | PRN: 2125UCSM1034 | Cyber Security Specialization")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_W - MARGIN, 0.9 * cm, page_str)

        self.restoreState()


def build_styles():
    styles = getSampleStyleSheet()

    title_cover = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    subtitle_cover = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=BLUE,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    h1 = ParagraphStyle(
        "ReportH1",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        "ReportH2",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=BLUE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body = ParagraphStyle(
        "ReportBody",
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=DARK_TEXT,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        "ReportBodyBold",
        parent=body,
        fontName="Helvetica-Bold"
    )

    th_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=white,
        alignment=TA_LEFT
    )

    td_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=DARK_TEXT,
        alignment=TA_LEFT
    )

    td_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10.5,
        textColor=NAVY,
        alignment=TA_LEFT
    )

    caption_style = ParagraphStyle(
        "FigCaption",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=BLUE,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=10
    )

    return {
        "title_cover": title_cover,
        "subtitle_cover": subtitle_cover,
        "h1": h1,
        "h2": h2,
        "body": body,
        "body_bold": body_bold,
        "th": th_style,
        "td": td_style,
        "td_bold": td_bold,
        "caption": caption_style
    }


def figure_box(img_path: str, caption: str, styles, max_w=CONTENT_W, max_h=180):
    """Embeds an image inside a neat border with caption."""
    if not os.path.exists(img_path):
        return Paragraph(f"[Image Missing: {os.path.basename(img_path)}]", styles["body"])
    
    ir = ImageReader(img_path)
    iw, ih = ir.getSize()
    scale = min(max_w / iw, max_h / ih)
    img = Image(img_path, width=iw * scale, height=ih * scale)
    img.hAlign = "CENTER"

    t = Table([[img]], colWidths=[iw * scale])
    t.hAlign = "CENTER"
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, LGREY),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether([t, Paragraph(caption, styles["caption"])])


def build_unit4_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    styles = build_styles()
    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>SANJIVANI UNIVERSITY, KOPARGAON</b>", styles["title_cover"]))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE ENGINEERING</b><br/>SPECIALIZATION IN CYBER SECURITY", styles["subtitle_cover"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2.2, color=NAVY, spaceBefore=4, spaceAfter=20))

    story.append(Paragraph("PRACTICAL ASSIGNMENT REPORT", styles["subtitle_cover"]))
    story.append(Paragraph("NPC – UNIT 4: CONFIGURE DHCP AND SET UP A NETWORK USING CISCO PACKET TRACER", styles["title_cover"]))
    story.append(Paragraph("Dynamic IPv4 Address Allocation, Pool Scoping, Service Verification & ICMP Connectivity Testing", styles["subtitle_cover"]))
    story.append(Spacer(1, 25))

    student_data = [
        [Paragraph("<b>Student Name</b>", styles["td"]), Paragraph("<b>Vishal Katyare</b>", styles["td"])],
        [Paragraph("<b>Permanent Registration Number (PRN)</b>", styles["td"]), Paragraph("<b>2125UCSM1034</b>", styles["td"])],
        [Paragraph("<b>Course / Degree</b>", styles["td"]), Paragraph("Bachelor of Technology (B.Tech)", styles["td"])],
        [Paragraph("<b>Department</b>", styles["td"]), Paragraph("Computer Science Engineering", styles["td"])],
        [Paragraph("<b>Specialization</b>", styles["td"]), Paragraph("Cyber Security", styles["td"])],
        [Paragraph("<b>Semester / Year</b>", styles["td"]), Paragraph("3rd Semester / Second Year (2026–2027)", styles["td"])],
        [Paragraph("<b>Subject / Module</b>", styles["td"]), Paragraph("Network Protocols and Communication (NPC – Unit 4)", styles["td"])],
        [Paragraph("<b>Institution</b>", styles["td"]), Paragraph("Sanjivani University, Kopargaon", styles["td"])],
        [Paragraph("<b>Repository URL</b>", styles["td"]), Paragraph("<font color='#2E5496'>https://github.com/vishal937/unit-4-npc.git</font>", styles["td"])],
    ]
    t_student = Table(student_data, colWidths=[6.0 * cm, CONTENT_W - 6.0 * cm])
    t_student.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), ROWBG),
        ("BACKGROUND", (1, 0), (1, -1), white),
        ("BOX", (0, 0), (-1, -1), 1, BLUE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LGREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_student)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: AIM & OBJECTIVES
    # =========================================================================
    story.append(Paragraph("1. Aim and Objectives", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))
    p_aim = (
        "<b>Aim:</b> To design and configure a Local Area Network (LAN) in Cisco Packet Tracer, assign a static IPv4 "
        "address to a central server, enable and configure the Dynamic Host Configuration Protocol (DHCP) service, "
        "dynamically allocate IP configurations to multiple client PCs, and verify end-to-end communication via ICMP ping."
    )
    story.append(Paragraph(p_aim, styles["body"]))

    p_obj = (
        "<b>Objectives:</b><br/>"
        "1. Deploy a network topology comprising 3 client PCs (<code>PC0</code>, <code>PC1</code>, <code>PC2</code>), "
        "a Cisco Catalyst 2960 Layer-2 switch (<code>Switch0</code>), and a generic DHCP server (<code>Server0</code>).<br/>"
        "2. Assign a static IPv4 address (<code>192.168.1.2/24</code>) to the DHCP server's FastEthernet0 interface.<br/>"
        "3. Enable the DHCP service daemon and configure a custom address pool named <code>NPC_POOL</code>.<br/>"
        "4. Transition client PCs from static IP configuration to dynamic DHCP allocation.<br/>"
        "5. Verify that client PCs automatically lease sequential IP addresses within the designated pool range.<br/>"
        "6. Test full bidirectional network connectivity across all client stations and the server using the ICMP <code>ping</code> utility."
    )
    story.append(Paragraph(p_obj, styles["body"]))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: HARDWARE & SOFTWARE SPECIFICATIONS
    # =========================================================================
    story.append(Paragraph("2. Hardware & Software Requirements", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))
    hw_data = [
        [Paragraph("<b>Component</b>", styles["th"]), Paragraph("<b>Device / Software</b>", styles["th"]), Paragraph("<b>Role & Configuration Description</b>", styles["th"])],
        [Paragraph("Simulation Software", styles["td_bold"]), Paragraph("Cisco Packet Tracer v9.0.1", styles["td"]), Paragraph("Virtual network modeling and packet simulation environment", styles["td"])],
        [Paragraph("DHCP Server", styles["td_bold"]), Paragraph("Generic Server-PT (Server0)", styles["td"]), Paragraph("Hosts the DHCP daemon; static IP 192.168.1.2/24", styles["td"])],
        [Paragraph("Layer-2 Switch", styles["td_bold"]), Paragraph("Cisco Catalyst 2960-24TT", styles["td"]), Paragraph("Connects nodes into single broadcast domain (VLAN 1)", styles["td"])],
        [Paragraph("Client Workstations", styles["td_bold"]), Paragraph("3 × Generic PC-PT (PC0, PC1, PC2)", styles["td"]), Paragraph("Dynamic DHCP clients receiving leased IP configurations", styles["td"])],
        [Paragraph("Physical Cabling", styles["td_bold"]), Paragraph("Copper Straight-Through (UTP)", styles["td"]), Paragraph("FastEthernet link connections between switch and endpoints", styles["td"])],
    ]
    t_hw = Table(hw_data, colWidths=[3.2 * cm, 4.2 * cm, CONTENT_W - 7.4 * cm])
    t_hw.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HDRBG),
        ("BOX", (0, 0), (-1, -1), 1, LGREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LGREY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROWBG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_hw)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: THEORETICAL FOUNDATION - DHCP DORA PROCESS
    # =========================================================================
    story.append(Paragraph("3. Theoretical Principles: The DHCP DORA Process", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))
    p_theory = (
        "The Dynamic Host Configuration Protocol (DHCP) operates at the Application Layer (utilizing UDP ports 67 and 68) "
        "to automate IP parameter assignment. When a client PC boots or enables DHCP, it undergoes the four-phase <b>DORA</b> exchange:<br/>"
        "• <b>Discover (DHCPDISCOVER):</b> The client broadcasts a layer-2 and layer-3 packet (Dest: <code>255.255.255.255</code>, "
        "<code>FF:FF:FF:FF:FF:FF</code>) searching for available DHCP servers on the local subnet.<br/>"
        "• <b>Offer (DHCPOFFER):</b> The DHCP server reserves an unassigned IP from its pool and broadcasts an offer containing "
        "the proposed IP address, subnet mask, default gateway, and lease duration.<br/>"
        "• <b>Request (DHCPREQUEST):</b> The client responds with a formal broadcast requesting the offered parameters and notifying "
        "other potential DHCP servers that their offers were declined.<br/>"
        "• <b>Acknowledge (DHCPACK):</b> The server commits the lease to its binding database and sends a unicast/broadcast acknowledgment, "
        "allowing the client to initialize its network interface."
    )
    story.append(Paragraph(p_theory, styles["body"]))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: NETWORK TOPOLOGY & ADDRESSING
    # =========================================================================
    story.append(Paragraph("4. Network Topology & DHCP Pool Parameters", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))

    pool_data = [
        [Paragraph("<b>Configuration Parameter</b>", styles["th"]), Paragraph("<b>Configured Value</b>", styles["th"]), Paragraph("<b>Operational Function</b>", styles["th"])],
        [Paragraph("Server0 IPv4 Address", styles["td_bold"]), Paragraph("<code>192.168.1.2</code>", styles["td"]), Paragraph("Static management IP address of the DHCP server", styles["td"])],
        [Paragraph("Subnet Mask", styles["td_bold"]), Paragraph("<code>255.255.255.0</code> (/24)", styles["td"]), Paragraph("Defines the local Class C broadcast network", styles["td"])],
        [Paragraph("DHCP Service State", styles["td_bold"]), Paragraph("<b>On</b>", styles["td"]), Paragraph("Enables the background DHCP listening daemon", styles["td"])],
        [Paragraph("Pool Name", styles["td_bold"]), Paragraph("<code>NPC_POOL</code>", styles["td"]), Paragraph("Designated identifier for the IP allocation scope", styles["td"])],
        [Paragraph("Start IP Address", styles["td_bold"]), Paragraph("<code>192.168.1.10</code>", styles["td"]), Paragraph("First assignable dynamic host address in the pool", styles["td"])],
        [Paragraph("Maximum Number of Users", styles["td_bold"]), Paragraph("<code>50</code>", styles["td"]), Paragraph("Restricts pool size to addresses 192.168.1.10 through .59", styles["td"])],
        [Paragraph("Default Gateway / DNS", styles["td_bold"]), Paragraph("<code>0.0.0.0</code>", styles["td"]), Paragraph("Single broadcast segment; external routing not required", styles["td"])],
    ]
    t_pool = Table(pool_data, colWidths=[4.0 * cm, 3.8 * cm, CONTENT_W - 7.8 * cm])
    t_pool.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HDRBG),
        ("BOX", (0, 0), (-1, -1), 1, LGREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LGREY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROWBG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_pool)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: STEP-BY-STEP CONFIGURATION PROCEDURE
    # =========================================================================
    story.append(Paragraph("5. Step-by-Step Configuration Procedure", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))
    p_steps = (
        "<b>Step 1 — Topology Deployment & Cabling:</b><br/>"
        "Place one Cisco 2960 switch (<code>Switch0</code>), one generic server (<code>Server0</code>), and three client PCs "
        "(<code>PC0</code>, <code>PC1</code>, <code>PC2</code>) in the Packet Tracer workspace. Connect each device using Copper "
        "Straight-Through Ethernet cables: Server0 to Fa0/1, PC0 to Fa0/2, PC1 to Fa0/3, and PC2 to Fa0/4.<br/><br/>"
        "<b>Step 2 — Static Server IP Assignment:</b><br/>"
        "Open Server0 ➔ <code>Desktop</code> ➔ <code>IP Configuration</code>. Select the <b>Static</b> radio button. Enter IPv4 Address "
        "<code>192.168.1.2</code> and Subnet Mask <code>255.255.255.0</code>.<br/><br/>"
        "<b>Step 3 — DHCP Service & Pool Configuration:</b><br/>"
        "Navigate to Server0 ➔ <code>Services</code> ➔ <code>DHCP</code>. Turn Service status to <b>On</b>. Set Pool Name to "
        "<code>NPC_POOL</code>, Start IP Address to <code>192.168.1.10</code>, Subnet Mask to <code>255.255.255.0</code>, and Maximum "
        "Number of Users to <code>50</code>. Click <b>Save</b> / <b>Add</b>.<br/><br/>"
        "<b>Step 4 — Client Dynamic Allocation:</b><br/>"
        "Open <code>Desktop</code> ➔ <code>IP Configuration</code> on PC0, PC1, and PC2 sequentially. Switch the configuration "
        "from Static to <b>DHCP</b>. Verify that Packet Tracer displays the prompt: <i>'DHCP request successful'</i>.<br/><br/>"
        "<b>Step 5 — End-to-End Connectivity Verification:</b><br/>"
        "Open PC0 Command Prompt and issue ICMP ping requests to Server0 (<code>192.168.1.2</code>), PC1 (<code>192.168.1.11</code>), "
        "and PC2 (<code>192.168.1.12</code>). Record transmission metrics and latency."
    )
    story.append(Paragraph(p_steps, styles["body"]))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 6: VISUAL EVIDENCE & EMBEDDED SCREENSHOTS
    # =========================================================================
    story.append(Paragraph("6. Visual Evidence & Configuration Screenshots", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))

    # Figure 1: Topology
    f1_path = os.path.join(SCREENSHOTS_DIR, "Figure_1_Network_Topology.png")
    story.append(figure_box(f1_path, "Figure 1: Complete Cisco Packet Tracer Network Topology with Operational Link Lights", styles))
    story.append(Spacer(1, 4))

    # Figure 2: Server Static IP
    f2_path = os.path.join(SCREENSHOTS_DIR, "Figure_2_Server0_Static_IP.png")
    story.append(figure_box(f2_path, "Figure 2: Server0 Static IPv4 Address Configuration (192.168.1.2 / 255.255.255.0)", styles))
    story.append(PageBreak())

    # Figure 3: DHCP Settings
    f3_path = os.path.join(SCREENSHOTS_DIR, "Figure_3_DHCP_Service_Settings.png")
    story.append(figure_box(f3_path, "Figure 3: Server0 DHCP Service Daemon Enabled with Custom NPC_POOL Parameters", styles))
    story.append(Spacer(1, 4))

    # Figure 4: PC0 DHCP
    f4_path = os.path.join(SCREENSHOTS_DIR, "Figure_4_PC0_DHCP_Config.png")
    story.append(figure_box(f4_path, "Figure 4: PC0 Dynamic IP Allocation via DHCP (Leased 192.168.1.10 Successfully)", styles))
    story.append(PageBreak())

    # Figure 5: PC1 DHCP
    f5_path = os.path.join(SCREENSHOTS_DIR, "Figure_5_PC1_DHCP_Config.png")
    story.append(figure_box(f5_path, "Figure 5: PC1 Dynamic IP Allocation via DHCP (Leased 192.168.1.11 Successfully)", styles))
    story.append(Spacer(1, 4))

    # Figure 6: PC2 DHCP
    f6_path = os.path.join(SCREENSHOTS_DIR, "Figure_6_PC2_DHCP_Config.png")
    story.append(figure_box(f6_path, "Figure 6: PC2 Dynamic IP Allocation via DHCP (Leased 192.168.1.12 Successfully)", styles))
    story.append(PageBreak())

    # Figure 7: Ping Test
    f7_path = os.path.join(SCREENSHOTS_DIR, "Figure_7_Ping_Connectivity_Test.png")
    story.append(figure_box(f7_path, "Figure 7: ICMP Ping Connectivity Test from PC0 to Server0, PC1, and PC2 (0% Loss)", styles))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 7: RESULTS, OBSERVATIONS & CONCLUSION
    # =========================================================================
    story.append(Paragraph("7. Results, Empirical Analysis & Conclusion", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))

    res_data = [
        [Paragraph("<b>Client Workstation</b>", styles["th"]), Paragraph("<b>Config Mode</b>", styles["th"]), Paragraph("<b>Dynamically Leased IP</b>", styles["th"]), Paragraph("<b>Subnet Mask</b>", styles["th"]), Paragraph("<b>Ping Verification (ICMP)</b>", styles["th"])],
        [Paragraph("PC0", styles["td_bold"]), Paragraph("DHCP", styles["td"]), Paragraph("<code>192.168.1.10</code>", styles["td"]), Paragraph("<code>255.255.255.0</code>", styles["td"]), Paragraph("<font color='#2E8B45'><b>4/4 Received (0% Loss, &lt;1ms)</b></font>", styles["td"])],
        [Paragraph("PC1", styles["td_bold"]), Paragraph("DHCP", styles["td"]), Paragraph("<code>192.168.1.11</code>", styles["td"]), Paragraph("<code>255.255.255.0</code>", styles["td"]), Paragraph("<font color='#2E8B45'><b>4/4 Received (0% Loss, &lt;1ms)</b></font>", styles["td"])],
        [Paragraph("PC2", styles["td_bold"]), Paragraph("DHCP", styles["td"]), Paragraph("<code>192.168.1.12</code>", styles["td"]), Paragraph("<code>255.255.255.0</code>", styles["td"]), Paragraph("<font color='#2E8B45'><b>4/4 Received (0% Loss, &lt;1ms)</b></font>", styles["td"])],
    ]
    t_res = Table(res_data, colWidths=[2.6 * cm, 2.4 * cm, 3.8 * cm, 3.6 * cm, CONTENT_W - 12.4 * cm])
    t_res.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HDRBG),
        ("BOX", (0, 0), (-1, -1), 1, LGREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LGREY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROWBG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_res)
    story.append(Spacer(1, 8))

    p_conc = (
        "<b>Conclusion:</b><br/>"
        "The practical assignment successfully demonstrated the automated provisioning of network parameters using "
        "Dynamic Host Configuration Protocol (DHCP) inside Cisco Packet Tracer. The central server (<code>Server0</code>) "
        "flawlessly leased sequential, non-conflicting IPv4 addresses to all client nodes. Subsequent ICMP ping testing confirmed "
        "complete layer-3 connectivity across all subnet stations with zero packet loss and sub-millisecond round-trip times. "
        "This experiment confirms that centralized DHCP administration eliminates manual IP assignment errors, prevents address "
        "collisions, and simplifies enterprise network scalability."
    )
    story.append(Paragraph(p_conc, styles["body"]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully compiled Unit 4 PDF report at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_unit4_pdf()
