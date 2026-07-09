.PHONY = run

run:
	uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

seed:
	python3 ./app/initial_data.py
