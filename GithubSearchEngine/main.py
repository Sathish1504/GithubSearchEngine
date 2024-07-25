import getDataFromGitHub as gdg
import tableProcessing as tproc
import pandas as pd
import gradio as gr




# The focus of this proyect is to obtain relevant data related to a given topic.
# How do we know what repositories are relevant? We want to value the repositories based 
# on the value they provide to the community.
# We can use the following criteria:
# - Number of stars 
# - Number of forks
# - Topics
# - Size
# - Language
# - Description
# - File types



def main(query, required_words, words_to_avoid, show_private, sort, ascending, entries_per_page, page, max_pages, ai_activated, min_star_limit):
    # query= "Java Interview Questions"
    # required_words = []
    # words_to_avoid = ["javascript"]
    # show_private = False
    # sort = "Stars"
    # ascending = False
    # entries_per_page = 10
    # page = 0
    # max_pages = 1
    # ai_activated = False

    # # Filtering options
    # min_star_limit = 10
    
    total_count = -1
    total_pages = 20

    current_datetime = pd.to_datetime("today").strftime("%Y-%m-%d_%H-%M-%S")

    document_name = f"{query}_{current_datetime}_rw_{required_words}_av_{words_to_avoid}_mp_{max_pages}"
    
    table = pd.DataFrame(columns=["Name","Repository Name", "Created Date","Language", "Stars","Forks Count","Score","Topics","Private","Owner Name", "URL", "Description","Size"])

    # Obtain the github query results
    while page <= total_pages and page != max_pages:
        table, metadata  = gdg.getData(table, query, page, entries_per_page)

        if total_count == -1:
            total_count = metadata["Total Count"]
            if total_count > 1000:
                total_count = 1000
            total_pages = total_count // entries_per_page
  
        page += 1

        print(f"Page {page} of {total_pages}")

    # Filter the results to find the relevant repositories based on custom criteria
    table = tproc.processTable(table, query,ai_activated,required_words, words_to_avoid,min_star_limit, show_private, sort, ascending)


    # Save results in an excel file
    table.to_excel(f"./Results/Excel/{document_name}.xlsx", index=False)

    cols_to_show = ["Name","Description","Topics","URL","Stars","Forks Count","Created Date","Language","Size"]

    # If AI is activated, append to cols_to_show the AI_Score column
    if ai_activated:
        cols_to_show.append("AI_Score")
 
    table_show = table.loc[:,cols_to_show]


    # Add the hyperlink from the URL column to the repository name
    table_show["Name"] = table_show["URL"].apply(lambda x: f'<a href="{x}">{x.split("/")[-1]}</a>')

    # Delete URL column
    table_show.drop(columns=["URL"], inplace=True)

    # format created date column
    table_show["Created Date"] = pd.to_datetime(table_show["Created Date"])
    table_show["Created Date"] = table_show["Created Date"].apply(lambda x: x.strftime("%Y-%m-%d"))

    # format size column
    table_show["Size"] = table_show["Size"].apply(lambda x: f"{x/1000:.2f} KB")

    # format topics column
    table_show["Topics"] = table_show["Topics"].apply(lambda x: ", ".join(x))

    # format description column if not none
    table_show["Description"] = table_show["Description"].apply(lambda x: "" if x is None else x)

    # format stars column
    table_show["Stars"] = table_show["Stars"].apply(lambda x: f"{x:,}")

    # format forks count column
    table_show["Forks Count"] = table_show["Forks Count"].apply(lambda x: f"{x:,}")

    # format AI score column
    if ai_activated:
        table_show["AI_Score"] = table_show["AI_Score"].apply(lambda x: f"{x:.2f}")
        

    # Make first column of fixed width
    table_show["Name"] = table_show["Name"].apply(lambda x: f'<div style="width: 200px">{x}</div>')

    # Convert to html
    table_show = table_show.to_html(escape=False, index=False)

    # Add css to the table
    # - Add white borders
    # - Add blue background
    # - Add padding to cells
    # - Center the text in the title
    # - Give light white background to the title

    table_show = f"""
    <style>
    table {{
        border: 1px solid white;
        text-align: center;
    }}
    
    th {{
        text-align: center;
        background-color: rgba(255,255,255,0.2);
    }}

    td {{
        padding: 10px;
    }}

    tr:nth-child(even) {{
        background-color: rgba(255,255,255,0.1);
    }}

    </style>
    {table_show}
    """

    







    return table_show


# Gradio interface with output below the inputs
with gr.Blocks(title="Results") as demo:
    # Add title
    gr.Markdown("# GitHub Repository Searcher")
    gr.Markdown("Search for repositories in GitHub and filter them based on custom criteria")
    query = gr.Textbox(label="Query", value="Python")
    with gr.Row():
        required_words = gr.Textbox(label="Required words")
        words_to_avoid = gr.Textbox(label="Words to avoid")
    with gr.Row():
        entries_per_page = gr.Slider(label="Entries per page", value=100)
        page = gr.Slider(label="Page", value=0)
        max_pages = gr.Slider(label="Max pages", value=5)
        min_star_limit = gr.Slider(label="Min star limit", value=10)

    
    with gr.Row():
        with gr.Column():
            sort = gr.Radio(label="Sort by", value="Stars",choices=["Stars","Forks Count","Created Date","Size"])
            greet_btn = gr.Button("Run!")
        with gr.Column():
            ascending = gr.Checkbox(label="Ascending")
            show_private = gr.Checkbox(label="Show private repositories")
            ai_activated = gr.Checkbox(label="AI activated")

    
    

    inputs = [query, required_words, words_to_avoid, show_private, sort, ascending, entries_per_page, page, max_pages, ai_activated, min_star_limit]
    
    # Output is an html
    outputs = gr.HTML()
    
     # Set function to be called when button is clicked
    greet_btn.click(fn=main, inputs=inputs, outputs=outputs)






if __name__ == "__main__":
    demo.launch()