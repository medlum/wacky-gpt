import streamlit as st
import streamlit_antd_components as sac


def breakingnews(news):
    """
    creates news ticker with CNAheadlines tools from utils
    """

    sac.alert(label='Breaking news...',
              description=news,
              size='md',
              radius='0px',
              # icon=True,
              variant='filled',
              closable=True,
              banner=[False, True])


def mode_button():
    """
    creates mode button 
    """
    return sac.segmented(
        items=[
            sac.SegmentedItem(label='creative'),
            sac.SegmentedItem(label='news'),
            sac.SegmentedItem(label='weather'),
            sac.SegmentedItem(label='finance'),
            sac.SegmentedItem(label='schedule'),

        ], align='center',
        size='xs',
        key='btn',
        divider=False,
        direction="vertical"
    )
