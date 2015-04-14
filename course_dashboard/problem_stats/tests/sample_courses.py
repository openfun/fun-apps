"""
Used to create course subtrees in ModuleStoreTestCase.create_test_course
"""

from collections import namedtuple

BlockInfo = namedtuple('BlockInfo', 'block_id, category, fields, sub_tree')

problem_block_info_tree = [  # pylint: disable=invalid-name
    BlockInfo(
        'chapter_x', 'chapter', {}, [
            BlockInfo(
                'sequential_x1', 'sequential', {}, [
                    BlockInfo(
                        'vertical_x1a', 'vertical', {}, [
                            BlockInfo('89b2ed2a06ce4f9f8dcd26fee087b60a', 'problem', {}, []),
                        ]
                    )
                ]
            )
        ]
    ),
]
