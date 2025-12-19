# QChainage Plugin - Simple Makefile
# No UI compilation needed - loads .ui files directly

PLUGINNAME = qchainage
PY_FILES = __init__.py qchainage.py qchainagedialog.py chainagetool.py qt_compat.py
UI_FILES = ui_qchainage.ui
EXTRAS = img/qchainage.png img/qchainage.svg metadata.txt
TRANSLATIONS = i18n/qchainage_de.ts i18n/qchainage_pt_PT.ts i18n/qchainage_fi.ts i18n/qchainage_pt_BR.ts

# Default target - nothing to compile
default:
	@echo "No compilation needed - UI files loaded directly at runtime"

# Deploy to QGIS 3 plugin directory
deploy: transcompile
	@echo "Deploying to QGIS 3 plugin directory..."
	mkdir -p $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/
	cp -vf $(UI_FILES) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/
	cp -vf $(EXTRAS) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/
	cp -vfr i18n $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/

# Create distribution package
package: transcompile
	@echo "Creating package..."
	rm -f $(PLUGINNAME).zip
	mkdir -p dist/$(PLUGINNAME)
	cp -f $(PY_FILES) dist/$(PLUGINNAME)/
	cp -f $(UI_FILES) dist/$(PLUGINNAME)/
	cp -f $(EXTRAS) dist/$(PLUGINNAME)/
	cp -rf i18n dist/$(PLUGINNAME)/
	cd dist && zip -r ../$(PLUGINNAME).zip $(PLUGINNAME)/
	rm -rf dist
	@echo "Package created: $(PLUGINNAME).zip"

# Compile translations
%.qm : %.ts
	lrelease $<

transcompile: $(TRANSLATIONS:.ts=.qm)

# Clean files
clean:
	rm -f i18n/*.qm
	rm -f $(PLUGINNAME).zip
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned compiled files and caches"

# Remove deployed plugin
remove-deploy:
	rm -rf $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)

# Help target
help:
	@echo "Available targets:"
	@echo "  deploy       - Deploy plugin to QGIS directory"
	@echo "  package      - Create distribution package"
	@echo "  transcompile - Compile translation files"
	@echo "  clean        - Clean compiled files"
	@echo "  remove-deploy- Remove deployed plugin"

.PHONY: default deploy package transcompile clean remove-deploy help
