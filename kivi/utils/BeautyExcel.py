import xlsxwriter
import seaborn as sns


class BeautyExcel:

    def __init__(self, df=None, dfs=None, path=None):
        """"""
        self.df = df
        self.dfs = dfs
        self.path = path
        # self.max_row, self.max_col = self.df.shape

        self.workbook = xlsxwriter.Workbook(self.path, {'nan_inf_to_errors': True})

    def get_pos(self, df, pos=None, start_row=0, start_col=0, interval=0, how='left'):
        """
        """
        if pos is not None and how == 'left':
            start_row, _, _, start_col = pos
            start_col += interval
        if pos is not None and how == 'bottom':
            _, start_col, start_row, _ = pos
            start_row += interval

        rows, cols = df.shape
        end_row = start_row + rows
        end_col = start_col + cols - 1
        return (start_row, start_col, end_row, end_col)

    def get_sheet(self, sheet_name):
        """"""
        try:
            return self.workbook.add_worksheet(sheet_name)
        except:
            return self.workbook.get_worksheet_by_name(sheet_name)

    def set_columns(self, df=None, columns=None):
        """"""
        if df is not None:
            columns = df.columns
        return [{'header': column} for column in columns]

    def set_rows_width(self, sheet_name, pos, width):
        """
        """
        self.get_sheet(sheet_name).set_row(pos, width)

    def set_columns_width(self, sheet_name, pos, width):
        """
        """
        if isinstance(pos, tuple):
            self.get_sheet(sheet_name).set_column(*pos, width)
        if isinstance(pos, str):
            self.get_sheet(sheet_name).set_column(pos, width)

    def set_header(self, sheet_name, text):
        """
        :text:
            - &[L, C, R]   位置
            - &[D, T]      时间
            - &[U, E]      下划线
            - &[], &G      图片占位符
            - &[F]         文件名
        """
        self.get_sheet(sheet_name).set_header(text)

    def set_data_bar(self, sheet_name, pos=None, column_name=None):
        """
        """
        if column_name is not None:
            column_id = self.columns.index(column_name)
            self.get_sheet(sheet_name).conditional_format(
                1, column_id, self.max_row, column_id, {'type': 'data_bar'})
        else:
            self.get_sheet(sheet_name).conditional_format(
                *pos, {'type': 'data_bar'})

    def add_text(self, ):
        """"""

    def gen_cell_format(self, palette='Paired', n_colors=None, desat=None, ):
        """
        """
        colormap = list(sns.color_palette(palette=palette, n_colors=n_colors, desat=desat).as_hex())
        cell_formats = [self.workbook.add_format({'bg_color': color}) for color in colormap]
        return cell_formats

    def set_condition_fromat(self, sheet_name, pos, criteria, value, cell_format, cell_type='cell', ):
        """
        描述： 添加条件

        :param type: `cell`, `data_bar`, `text`
        :param criteria: `>`, `=`, `>=`, `<=`, `containing`
        :param value: value
        :param cell_format: cell_format
        """
        param = {
            'type': cell_type,
            'criteria': criteria,
            'value': value,
            'format': cell_format,
        }

        self.get_sheet(sheet_name).conditional_format(
            *pos, param)

    def add_url(self, sheet_name, pos, url, string=None):
        """
        描述：
            - eg: internal:Sheet2!A1
            - eg: internal:Sheet2!A1
        """
        if string is None:
            string = url
        if isinstance(pos, tuple):
            self.get_sheet(sheet_name).write_url(*pos, url, string=string)
        if isinstance(pos, str):
            self.get_sheet(sheet_name).write_url(pos, url, string=string)

    def add_img(
            self, sheet_name, row, col, filename, shift=(0, 0), scale=(1, 1),
            object_position=2, image_data=None, url=None, description=None,
            decorative=False):
        """"""

        x_offset, y_offset = shift
        x_scale, y_scale = scale

        param = {
            'x_offset': x_offset,
            'y_offset': y_offset,
            'x_scale': x_scale,
            'y_scale': y_scale,
            'object_position': object_position,
            'image_data': image_data,
            'url': url,
            'description': description,
            'decorative': decorative,
        }

        self.get_sheet(sheet_name).insert_image(row, col, filename, param)

    def add_table(self, df=None, sheet_name=None, pos=None, param=None, style='Table Style Light 8'):
        """

        """
        if sheet_name is None:
            sheet_name = 'Sheet'

        if pos is None:
            start_row, start_col = 0, 0
            end_row, end_col = df.shape
            end_col -= 1
        else:
            start_row, start_col, end_row, end_col = pos

        if param is None:
            param = {
                'data': df.values.tolist(),
                'columns': self.set_columns(df=df),
                'style': style,
            }

        self.get_sheet(sheet_name).add_table(
            start_row, start_col, end_row, end_col, param)

    def group(self, df, sheet_name, by, sort_by=None, ascending=False, pos=(0, 0), style=None, interval=1):
        """
        描述：分组展示统计项

        参数：
        :param style:
            - Table Style Light 1-21
            - Table Style Medium 1-28
            - Table Style Dark 1-11
        """
        param = {
            'data': None,
            'columns': self.set_columns(df=df),
            'style': style,
        }
        start_row, start_col = pos

        for group_name, df_group in df.groupby(by):
            if sort_by:
                df_group = df_group.sort_values(by=sort_by, ascending=ascending)
            param['data'] = df_group.values.tolist()
            rows, cols = df_group.shape
            end_row, end_col = start_row + rows, start_col + cols - 1
            self.add_table(df_group, sheet_name=sheet_name,
                           pos=(start_row, start_col, end_row, end_col), param=param)
            start_row = start_row + rows + 1 + interval
