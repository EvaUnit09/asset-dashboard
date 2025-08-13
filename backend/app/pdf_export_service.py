"""
PDF Export Service for generating professional asset management reports.
Uses ReportLab for PDF generation and integrates with ChartGenerator.
"""

import json
from io import BytesIO
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from collections import Counter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import Asset, ExportConfig, TableFilters, ExportHistory
from .chart_generator import ChartGenerator


class PDFExportService:
    """Service for generating PDF exports of asset management data."""
    
    def __init__(self, assets: List[Asset], config: ExportConfig):
        """
        Initialize PDF export service.
        
        Args:
            assets: List of Asset objects to include in export
            config: Export configuration specifying what to include
        """
        self.assets = assets
        self.config = config
        self.chart_generator = ChartGenerator()
        self.styles = self._setup_styles()
        self.logger = logging.getLogger(__name__)
        # Margins in points (72 pt = 1 inch)
        self.left_margin = 72
        self.right_margin = 72
        self.top_margin = 72
        self.bottom_margin = 72
        
        # Set page size and orientation
        if config.pageSize.upper() == 'A4':
            page_size = A4
        else:
            page_size = letter
            
        if config.orientation.lower() == 'landscape':
            self.page_size = landscape(page_size)
        else:
            self.page_size = portrait(page_size)
        try:
            page_w, page_h = self.page_size
        except Exception:
            page_w, page_h = (None, None)
        self.logger.info(
            "PDFExportService initialized",
            extra={
                'page_size': config.pageSize,
                'orientation': config.orientation,
                'computed_page_width': page_w,
                'computed_page_height': page_h,
                'asset_count': len(self.assets)
            }
        )
    
    def generate_pdf(self) -> BytesIO:
        """
        Generate PDF document based on configuration.
        
        Returns:
            BytesIO buffer containing the PDF document
        """
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.right_margin,
            leftMargin=self.left_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title=self.config.title
        )
        
        # Build document content
        story = []
        
        # Add header/title section
        story.extend(self._build_header())
        
        # Add filter information if requested
        if self.config.includeFilters and self.config.tableFilters:
            story.extend(self._build_filters_section())
        
        # Add summary section if requested
        if self.config.includeSummary:
            story.extend(self._build_summary_section())
            
        # Add charts section if requested
        if self.config.includeCharts and self.config.selectedCharts:
            story.extend(self._build_charts_section())
            
        # Asset details table removed from PDF - use Excel export instead
        # This improves PDF readability and provides better interaction with data
            
        # Add footer with timestamp if requested
        if self.config.includeTimestamp:
            story.extend(self._build_footer())
        
        # Build PDF
        try:
            self.logger.info(
                "Building PDF document",
                extra={
                    'story_items': len(story),
                    'include_summary': self.config.includeSummary,
                    'include_charts': self.config.includeCharts,
                    'selected_charts': self.config.selectedCharts,
                    'include_filters': self.config.includeFilters and bool(self.config.tableFilters)
                }
            )
            doc.build(story)
        except Exception:
            # Log full stack trace with configuration for troubleshooting
            try:
                config_json = json.dumps(self.config.model_dump())
            except Exception:
                config_json = "<unserializable>"
            self.logger.exception(
                "Failed to build PDF document",
                extra={
                    'export_config': config_json,
                    'asset_count': len(self.assets)
                }
            )
            raise
        buffer.seek(0)
        
        return buffer
    
    def _setup_styles(self) -> Dict[str, ParagraphStyle]:
        """Set up custom paragraph styles for the PDF."""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1f2937')
            ),
            'heading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=20,
                spaceBefore=30,
                textColor=colors.HexColor('#1f2937')
            ),
            'heading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=15,
                spaceBefore=20,
                textColor=colors.HexColor('#374151')
            ),
            'normal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                textColor=colors.HexColor('#4b5563')
            ),
            'small': ParagraphStyle(
                'CustomSmall',
                parent=styles['Normal'],
                fontSize=8,
                spaceAfter=4,
                textColor=colors.HexColor('#6b7280')
            ),
            'footer': ParagraphStyle(
                'CustomFooter',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#9ca3af')
            )
        }
        
        return custom_styles
    
    def _build_header(self) -> List:
        """Build the header section of the PDF."""
        story = []
        
        # Main title
        title = Paragraph(self.config.title, self.styles['title'])
        story.append(title)
        
        # Description if provided
        if self.config.description:
            desc = Paragraph(self.config.description, self.styles['normal'])
            story.append(desc)
            story.append(Spacer(1, 12))
        
        # Report metadata
        metadata_data = [
            ['Generated on:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Total Assets:', str(len(self.assets))],
            ['Page Size:', self.config.pageSize],
            ['Orientation:', self.config.orientation.title()]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[1.5*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#4b5563')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_filters_section(self) -> List:
        """Build the filters information section."""
        story = []
        filters = self.config.tableFilters
        
        if not filters:
            return story
        
        story.append(Paragraph("Applied Filters", self.styles['heading2']))
        
        filter_data = []
        if filters.company:
            filter_data.append(['Company:', filters.company])
        if filters.manufacturer:
            filter_data.append(['Manufacturer:', filters.manufacturer])
        if filters.category:
            filter_data.append(['Category:', filters.category])
        if filters.model:
            filter_data.append(['Model:', filters.model])
        if filters.department:
            filter_data.append(['Department:', filters.department])
        if filters.searchQuery:
            filter_data.append(['Search Query:', filters.searchQuery])
        
        if filter_data:
            filter_table = Table(filter_data, colWidths=[1.5*inch, 4*inch])
            filter_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#4b5563')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(filter_table)
        else:
            story.append(Paragraph("No filters applied", self.styles['normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _build_summary_section(self) -> List:
        """Build the summary statistics section."""
        story = []
        
        story.append(Paragraph("Summary Statistics", self.styles['heading1']))
        
        # Calculate statistics
        stats = self._calculate_statistics()
        
        # Create summary cards layout
        summary_data = []
        if 'total' in self.config.summaryCards:
            summary_data.append(['Total Assets', str(stats['total'])])
        if 'active' in self.config.summaryCards:
            summary_data.append(['Active Assets', str(stats['active'])])
        if 'pending' in self.config.summaryCards:
            summary_data.append(['Pending Rebuild', str(stats['pending'])])
        if 'stock' in self.config.summaryCards:
            summary_data.append(['In Stock', str(stats['stock'])])
        
        if summary_data:
            # Create a 2x2 grid for summary cards
            if len(summary_data) <= 2:
                cols = len(summary_data)
                grid_data = [summary_data]
            else:
                cols = 2
                grid_data = []
                for i in range(0, len(summary_data), cols):
                    row = summary_data[i:i+cols]
                    # Pad row if needed
                    while len(row) < cols:
                        row.append(['', ''])
                    grid_data.append(row)
            
            # Flatten the grid for table
            table_data = []
            for row in grid_data:
                labels = [item[0] for item in row]
                values = [item[1] for item in row]
                table_data.append(labels)
                table_data.append(values)
            
            col_width = (6 * inch) / cols
            summary_table = Table(table_data, colWidths=[col_width] * cols)
            summary_table.setStyle(TableStyle([
                # Label rows (even indices)
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
                ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f9fafb')),
                # Value rows (odd indices)
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 18),
                ('FONTSIZE', (0, 3), (-1, 3), 18),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#3b82f6')),
                # General styling
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(summary_table)
        
        story.append(Spacer(1, 30))
        return story
    
    def _build_charts_section(self) -> List:
        """Build the charts section with selected charts."""
        story = []
        
        # Ensure charts start on a fresh page to avoid layout issues when
        # the remaining space on the current page is insufficient (e.g. landscape).
        # Only break if there is already content in the story to avoid blank page at start.
        story.append(PageBreak())
        story.append(Paragraph("Charts and Analytics", self.styles['heading1']))
        
        for i, chart_type in enumerate(self.config.selectedCharts):
            # Add page break before each chart except the first
            if i > 0:
                story.append(PageBreak())
            
            # Add chart with title on its own page
            if chart_type == 'category':
                story.extend(self._add_chart(
                    "Assets by Category",
                    self.chart_generator.generate_category_chart(self.assets)
                ))
            elif chart_type == 'status':
                story.extend(self._add_chart(
                    "Status Distribution",
                    self.chart_generator.generate_status_pie_chart(self.assets)
                ))
            elif chart_type == 'trends':
                story.extend(self._add_chart(
                    "Monthly Asset Trends",
                    self.chart_generator.generate_trends_chart(self.assets)
                ))
            elif chart_type == 'warranty':
                story.extend(self._add_chart(
                    "Warranty Expiration Trends",
                    self.chart_generator.generate_warranty_expiration_chart(self.assets)
                ))
        
        return story
    
    def _add_chart(self, title: str, chart_buffer: BytesIO) -> List:
        """Add a chart to the story with proper formatting."""
        story = []
        
        # Chart title
        story.append(Paragraph(title, self.styles['heading2']))
        story.append(Spacer(1, 12))
        
        # Chart image
        try:
            img = Image(chart_buffer)
            # Compute available space based on page size and margins
            page_width, page_height = self.page_size
            max_width = max(page_width - (self.left_margin + self.right_margin), 1)
            # Reserve height for title + spacer above the image
            reserved_above = 1.25 * inch
            max_height = max(page_height - (self.top_margin + self.bottom_margin) - reserved_above, 1)

            intrinsic_width = float(img.imageWidth)
            intrinsic_height = float(img.imageHeight)
            scale_w = max_width / intrinsic_width
            scale_h = max_height / intrinsic_height
            scale = min(scale_w, scale_h, 1.0)

            img.drawWidth = intrinsic_width * scale
            img.drawHeight = intrinsic_height * scale

            # Log sizing for troubleshooting layout errors
            self.logger.info(
                "Chart image sizing",
                extra={
                    'page_width': page_width,
                    'page_height': page_height,
                    'max_width': max_width,
                    'max_height': max_height,
                    'intrinsic_width': intrinsic_width,
                    'intrinsic_height': intrinsic_height,
                    'draw_width': img.drawWidth,
                    'draw_height': img.drawHeight,
                }
            )

            story.append(img)
            story.append(Spacer(1, 20))
        except Exception as e:
            # Fallback if chart generation fails
            error_text = Paragraph(f"Chart could not be generated: {str(e)}", self.styles['small'])
            story.append(error_text)
            story.append(Spacer(1, 20))
        
        return story
    
    def _build_table_section(self) -> List:
        """Build the asset table section."""
        story = []
        
        story.append(Paragraph("Asset Details", self.styles['heading1']))
        
        # Filter assets if table filters are specified
        filtered_assets = self._apply_table_filters()
        
        if not filtered_assets:
            story.append(Paragraph("No assets match the specified criteria.", self.styles['normal']))
            return story
        
        # Limit to first 100 assets for PDF readability
        display_assets = filtered_assets[:100]
        if len(filtered_assets) > 100:
            truncate_msg = f"Showing first 100 of {len(filtered_assets)} assets."
            story.append(Paragraph(truncate_msg, self.styles['small']))
            story.append(Spacer(1, 10))
        
        # Build table data
        headers = [col.replace('_', ' ').title() for col in self.config.tableColumns]
        table_data = [headers]
        
        for asset in display_assets:
            row = []
            for col in self.config.tableColumns:
                value = getattr(asset, col, '') or ''
                # Truncate long values
                if len(str(value)) > 30:
                    value = str(value)[:27] + '...'
                row.append(str(value))
            table_data.append(row)
        
        # Create table
        col_width = (7 * inch) / len(self.config.tableColumns)
        asset_table = Table(table_data, colWidths=[col_width] * len(self.config.tableColumns))
        
        # Style table
        table_style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#4b5563')),
            
            # General styling
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Alternate row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fafafa')))
        
        asset_table.setStyle(TableStyle(table_style))
        story.append(asset_table)
        
        return story
    
    def _build_footer(self) -> List:
        """Build the footer section with timestamp."""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 10))
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        footer_text = f"Generated on {timestamp} by Asset Management System"
        footer = Paragraph(footer_text, self.styles['footer'])
        story.append(footer)
        
        return story
    
    def _calculate_statistics(self) -> Dict[str, int]:
        """Calculate summary statistics for the assets."""
        # Filter assets to match dashboard (Active, Stock, Pending Rebuild only)
        filtered_assets = [a for a in self.assets if a.status in ['Active', 'Stock', 'Pending Rebuild']]
        
        stats = {
            'total': len(filtered_assets),
            'active': len([a for a in filtered_assets if a.status == 'Active']),
            'pending': len([a for a in filtered_assets if a.status == 'Pending Rebuild']),
            'stock': len([a for a in filtered_assets if a.status == 'Stock'])
        }
        
        return stats
    
    def _apply_table_filters(self) -> List[Asset]:
        """Apply table filters to the asset list."""
        if not self.config.tableFilters:
            return self.assets
        
        filtered = self.assets
        filters = self.config.tableFilters
        
        if filters.company:
            filtered = [a for a in filtered if a.company and filters.company.lower() in a.company.lower()]
        
        if filters.manufacturer:
            filtered = [a for a in filtered if a.manufacturer and filters.manufacturer.lower() in a.manufacturer.lower()]
        
        if filters.category:
            filtered = [a for a in filtered if a.category and filters.category.lower() in a.category.lower()]
        
        if filters.model:
            filtered = [a for a in filtered if a.model and filters.model.lower() in a.model.lower()]
        
        if filters.department:
            filtered = [a for a in filtered if a.department and filters.department.lower() in a.department.lower()]
        
        if filters.searchQuery:
            query = filters.searchQuery.lower()
            filtered = [a for a in filtered if any([
                a.asset_name and query in a.asset_name.lower(),
                a.asset_tag and query in a.asset_tag.lower(),
                a.serial and query in a.serial.lower(),
                a.location and query in a.location.lower(),
            ])]
        
        return filtered 