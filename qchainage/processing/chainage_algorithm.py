# -*- coding: utf-8 -*-
"""
QChainage Processing Algorithm
Creates points at specified intervals along line geometries.

Copyright (c) 2025-2026 Werner Macho
Licensed under GNU GPL v3.0
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDistance,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsUnitTypes,
    QgsWkbTypes,
)

try:
    from ..chainagetool import create_points
except (ImportError, ValueError):
    try:
        from qchainage.chainagetool import create_points
    except (ImportError, ValueError):
        from chainagetool import create_points


class QChainageAlgorithm(QgsProcessingAlgorithm):
    """QChainage algorithm for the QGIS Processing framework."""

    INPUT = 'INPUT'
    DISTANCE = 'DISTANCE'
    DISTANCE_UNITS = 'DISTANCE_UNITS'
    START_DISTANCE = 'START_DISTANCE'
    END_DISTANCE = 'END_DISTANCE'
    DIVIDE = 'DIVIDE'
    FORCE_LAST = 'FORCE_LAST'
    ONLY_FIRST_LAST = 'ONLY_FIRST_LAST'
    REVERSE = 'REVERSE'
    USE_ELLIPSOIDAL = 'USE_ELLIPSOIDAL'
    CALCULATE_ANGLE = 'CALCULATE_ANGLE'
    FIELDS_TO_COPY = 'FIELDS_TO_COPY'
    OUTPUT = 'OUTPUT'

    UNITS_MAP = [
        None,  # 0: Layer units
        QgsUnitTypes.DistanceMeters,        # 1: Meters
        QgsUnitTypes.DistanceKilometers,    # 2: Kilometers
        QgsUnitTypes.DistanceFeet,          # 3: Feet
        QgsUnitTypes.DistanceMiles,         # 4: Miles
        QgsUnitTypes.DistanceYards,         # 5: Yards
        QgsUnitTypes.DistanceCentimeters,   # 6: Centimeters
        QgsUnitTypes.DistanceMillimeters,   # 7: Millimeters
    ]

    def tr(self, string: str) -> str:
        return QCoreApplication.translate('QChainageAlgorithm', string)

    def createInstance(self):
        return QChainageAlgorithm()

    def name(self) -> str:
        return 'points_along_lines'

    def displayName(self) -> str:
        return self.tr('Points along lines (Chainage)')

    def group(self) -> str:
        return self.tr('Vector geometry')

    def groupId(self) -> str:
        return 'vectorgeometry'

    def shortHelpString(self) -> str:
        return self.tr(
            "Creates point features at regular intervals along input lines."
            "\n\nFeatures include:\n"
            "- Flexible intervals in various units (meters, feet, km, etc.)\n"
            "- Equal division into N parts\n"
            "- Custom start and end offset distances\n"
            "- Normal or reversed chainage direction\n"
            "- Cartesian or ellipsoidal distance measurement\n"
            "- Optional calculation of tangent line bearing/angle (0-360°)\n"
            "- Attribute preservation from source lines\n"
            "- Full 3D (Z) and M dimension support."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input line layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterDistance(
                self.DISTANCE,
                self.tr('Interval distance'),
                defaultValue=10.0,
                parentParameterName=self.INPUT
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.DISTANCE_UNITS,
                self.tr('Distance units'),
                options=[
                    self.tr('Layer units'),
                    self.tr('Meters'),
                    self.tr('Kilometers'),
                    self.tr('Feet'),
                    self.tr('Miles'),
                    self.tr('Yards'),
                    self.tr('Centimeters'),
                    self.tr('Millimeters'),
                ],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterDistance(
                self.START_DISTANCE,
                self.tr('Start point (offset from beginning)'),
                defaultValue=0.0,
                parentParameterName=self.INPUT,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterDistance(
                self.END_DISTANCE,
                self.tr('End point (stop before line end, 0 = end of line)'),
                defaultValue=0.0,
                parentParameterName=self.INPUT,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIVIDE,
                self.tr('Divide into N equal parts (0 = use distance)'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0,
                minValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.FORCE_LAST,
                self.tr('Force endpoint to be created'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ONLY_FIRST_LAST,
                self.tr('Create only first and last points'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.REVERSE,
                self.tr('Reverse chainage direction (start from end)'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_ELLIPSOIDAL,
                self.tr('Use ellipsoidal (geodesic) distance measurement'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CALCULATE_ANGLE,
                self.tr('Calculate angle / bearing along line'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELDS_TO_COPY,
                self.tr('Fields to copy from source layer'),
                parentLayerParameterName=self.INPUT,
                allowMultiple=True,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Chainage points'),
                type=QgsProcessing.TypeVectorPoint
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise ValueError(self.tr('Invalid input layer'))

        distance = self.parameterAsDouble(parameters, self.DISTANCE, context)
        unit_idx = self.parameterAsEnum(
            parameters, self.DISTANCE_UNITS, context
        )
        if unit_idx < len(self.UNITS_MAP):
            distance_units = self.UNITS_MAP[unit_idx]
        else:
            distance_units = None

        if distance_units is None:
            distance_units = source.sourceCrs().mapUnits()

        startpoint = self.parameterAsDouble(
            parameters, self.START_DISTANCE, context
        )
        endpoint = self.parameterAsDouble(
            parameters, self.END_DISTANCE, context
        )
        divide = self.parameterAsInt(parameters, self.DIVIDE, context)
        force_last = self.parameterAsBoolean(
            parameters, self.FORCE_LAST, context
        )
        force_first_last = self.parameterAsBoolean(
            parameters, self.ONLY_FIRST_LAST, context
        )
        reverse = self.parameterAsBoolean(
            parameters, self.REVERSE, context
        )
        use_ellipsoidal = self.parameterAsBoolean(
            parameters, self.USE_ELLIPSOIDAL, context
        )
        include_angle = self.parameterAsBoolean(
            parameters, self.CALCULATE_ANGLE, context
        )
        if hasattr(self, 'parameterAsStrings'):
            fields_to_copy = self.parameterAsStrings(
                parameters, self.FIELDS_TO_COPY, context
            )
        else:
            fields_to_copy = self.parameterAsFields(
                parameters, self.FIELDS_TO_COPY, context
            )

        # Build output fields
        unit_str = QgsUnitTypes.toString(distance_units)
        dist_field_name = f"cng_{unit_str}"

        out_fields = QgsFields()
        out_fields.append(QgsField(dist_field_name, QVariant.Double))
        if include_angle:
            out_fields.append(QgsField("angle", QVariant.Double))

        if fields_to_copy:
            source_fields = source.fields()
            for fld_name in fields_to_copy:
                fld = source_fields.field(fld_name)
                if fld:
                    out_fields.append(QgsField(fld.name(), fld.type()))

        # Determine output geometry WKB type
        wkb_type = QgsWkbTypes.Point
        if QgsWkbTypes.hasZ(source.wkbType()):
            wkb_type = QgsWkbTypes.addZ(wkb_type)
        if QgsWkbTypes.hasM(source.wkbType()):
            wkb_type = QgsWkbTypes.addM(wkb_type)

        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            out_fields,
            wkb_type,
            source.sourceCrs()
        )
        if sink is None:
            raise ValueError(self.tr('Could not create output sink'))

        total_features = source.featureCount()
        current_feat_idx = 0

        for feature in source.getFeatures():
            if feedback.isCanceled():
                break

            geom = feature.geometry()
            if geom and not geom.isEmpty():
                points = create_points(
                    startpoint=startpoint,
                    endpoint=endpoint,
                    distance=distance,
                    geom=geom,
                    force_last=force_last,
                    force_first_last=force_first_last,
                    divide=divide,
                    layer_crs=source.sourceCrs(),
                    use_ellipsoidal=use_ellipsoidal,
                    distance_units=distance_units,
                    source_feature=feature,
                    copy_attributes=fields_to_copy,
                    reverse=reverse,
                    include_angle=include_angle,
                    dist_field_name=dist_field_name
                )
                for pt_feat in points:
                    sink.addFeature(pt_feat, QgsFeatureSink.FastInsert)

            current_feat_idx += 1
            if total_features > 0:
                percent = int((current_feat_idx / total_features) * 100)
                feedback.setProgress(percent)

        return {self.OUTPUT: dest_id}
