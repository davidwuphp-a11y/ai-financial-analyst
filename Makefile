.PHONY: install run test eval preview clean

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	pytest tests/ -q

eval:
	python evaluate.py

preview:
	cd assets && python make_preview.py

clean:
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
