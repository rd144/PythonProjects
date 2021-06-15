INSERT INTO {{table}}
(
	{{columns}}
)
SELECT
	*
FROM
(
VALUES
	{{values}}
);