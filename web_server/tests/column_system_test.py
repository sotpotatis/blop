from .content_renderer.screen.element import Column, Row, Justify

#Test: Create a row
row = Row(
    [Column(
        elements=[
            "Hello",
            "ASCII Art"
        ]
    ),
        Column(
            elements=[
                "Apples",
                "Multiline\nText\nWorks\nToo"
            ]
        )
    ],
    80,
    24,
    Justify.CENTER,
    Justify.CENTER
)
print(str(row))